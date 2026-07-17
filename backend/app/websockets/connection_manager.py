import logging
from fastapi import WebSocket
from typing import Dict, Set

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages active student and teacher WebSocket connections mapped by room/session UUIDs.
    Handles broadcasts, direct sends, and memory cleanup.
    """

    def __init__(self):
        # Maps session_id string -> Set of active student websockets
        self.active_students: Dict[str, Set[WebSocket]] = {}
        # Maps session_id string -> Teacher/Host websocket
        self.active_teachers: Dict[str, WebSocket] = {}

    async def connect_student(self, room_id: str, websocket: WebSocket):
        """
        Accept and register a student socket to a room.
        """
        await websocket.accept()
        if room_id not in self.active_students:
            self.active_students[room_id] = set()
        self.active_students[room_id].add(websocket)
        logger.info(
            f"Student joined WebSocket room {room_id}. Current students count: {len(self.active_students[room_id])}"
        )

    async def connect_teacher(self, room_id: str, websocket: WebSocket):
        """
        Accept and register a teacher socket as the room coordinator.
        """
        await websocket.accept()
        self.active_teachers[room_id] = websocket
        logger.info(f"Teacher joined WebSocket room {room_id} as coordinator.")

    def disconnect_student(self, room_id: str, websocket: WebSocket):
        """
        Deregister a student socket. Performs room memory cleanup if empty.
        """
        if room_id in self.active_students:
            self.active_students[room_id].discard(websocket)
            logger.info(
                f"Student left WebSocket room {room_id}. Remaining: {len(self.active_students[room_id])}"
            )
            if not self.active_students[room_id] and room_id not in self.active_teachers:
                del self.active_students[room_id]
                logger.info(f"Garbage collected empty room registry: {room_id}")

    def disconnect_teacher(self, room_id: str):
        """
        Deregister the teacher socket. Performs room memory cleanup if empty.
        """
        if room_id in self.active_teachers:
            del self.active_teachers[room_id]
            logger.info(f"Teacher coordinator left room {room_id}")
            if room_id in self.active_students and not self.active_students[room_id]:
                del self.active_students[room_id]
                logger.info(f"Garbage collected empty room registry: {room_id}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """
        Send a private message to a specific connection.
        """
        await websocket.send_json(message)

    async def broadcast_to_room(self, room_id: str, message: dict):
        """
        Broadcast a payload to all connected students and the coordinator in the room.
        """
        if room_id in self.active_students:
            for connection in list(self.active_students[room_id]):
                try:
                    await connection.send_json(message)
                except Exception:
                    self.disconnect_student(room_id, connection)

        if room_id in self.active_teachers:
            try:
                await self.active_teachers[room_id].send_json(message)
            except Exception:
                self.disconnect_teacher(room_id)


manager = ConnectionManager()
