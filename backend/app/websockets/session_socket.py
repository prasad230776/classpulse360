import logging
import jwt
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.core.security import decode_token
from app.repositories.user_repository import user_repository
from app.services.session_service import session_service
from app.websockets.connection_manager import manager
from app.websockets.events import WebSocketEventType
from app.common.enums import UserRole

logger = logging.getLogger(__name__)

ws_router = APIRouter()


@ws_router.websocket("/ws/session/{room_code}")
async def session_websocket(
    websocket: WebSocket,
    room_code: str,
    token: Optional[str] = Query(None),
):
    """
    WebSocket endpoint handling real-time interactive quiz sessions.
    Validates user tokens, maps roles to correct manager registries,
    broadcasts presence events, and handles disconnect cleanups.
    """
    db: Session = SessionLocal()
    try:
        # 1. Require JWT authentication token
        if not token:
            logger.warning("WebSocket connection rejected: Missing token.")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        try:
            payload = decode_token(token)
            user_id = payload.get("sub")
            if not user_id:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                return
        except jwt.PyJWTError:
            logger.warning("WebSocket connection rejected: Invalid token.")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        user = user_repository.get_by_id(db, id=user_id)
        if not user or not user.is_active:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        # 2. Fetch target Session room by code
        try:
            session = session_service.get_session_by_room_code(db, room_code=room_code)
        except Exception:
            logger.warning(f"WebSocket connection rejected: Room {room_code} not found.")
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
            return

        room_id_str = str(session.id)

        # 3. Route connection based on user Role
        if user.role in [UserRole.TEACHER, UserRole.ADMIN]:
            await manager.connect_teacher(room_id_str, websocket)
            is_teacher = True
        else:
            await manager.connect_student(room_id_str, websocket)
            is_teacher = False

        # 4. Broadcast join presence event
        if not is_teacher:
            await manager.broadcast_to_room(
                room_id_str,
                {
                    "event": WebSocketEventType.PARTICIPANT_JOINED.value,
                    "data": {"user_id": str(user.id), "name": user.name},
                },
            )

        # 5. Enter active socket listener loop
        try:
            while True:
                # Keep connection alive; accept potential client-side message commands
                data = await websocket.receive_json()
                logger.debug(f"Received WebSocket message from room {room_code}: {data}")
        except WebSocketDisconnect:
            # 6. Tear down connection on client disconnect
            if is_teacher:
                manager.disconnect_teacher(room_id_str)
            else:
                manager.disconnect_student(room_id_str, websocket)
                await manager.broadcast_to_room(
                    room_id_str,
                    {
                        "event": WebSocketEventType.PARTICIPANT_LEFT.value,
                        "data": {"user_id": str(user.id), "name": user.name},
                    },
                )
    finally:
        db.close()
