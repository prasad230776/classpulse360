from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel, Field

from app.api.responses import APIResponse
from app.schemas.session import SessionCreate, SessionResponse
from app.schemas.participant import ParticipantResponse
from app.schemas.question import QuestionResponse
from app.services.session_service import session_service
from app.services.question_service import question_service
from app.database.session import get_db
from app.api.v1.dependencies.auth import get_current_user, require_role
from app.common.enums import UserRole, SessionStatus
from app.websockets import connection_manager
from app.websockets.events import WebSocketEventType

session_router = APIRouter()


class ActivateQuestionRequest(BaseModel):
    question_id: UUID = Field(..., description="UUID of the question to set active")


class RoomStatusResponse(BaseModel):
    session_id: UUID = Field(..., description="UUID of the active session")
    room_code: Optional[str] = Field(None, description="Unique alphanumeric code used to join")
    status: SessionStatus = Field(..., description="Current execution state of the session")
    active_question_id: Optional[UUID] = Field(None, description="Currently active question UUID")


@session_router.post(
    "/",
    response_model=APIResponse[SessionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create a new quiz session",
    dependencies=[Depends(require_role(UserRole.TEACHER))],
)
async def create_session(obj_in: SessionCreate, db: Session = Depends(get_db)):
    """
    Launch a new session room (restricted to teachers). Room code is auto-generated.
    """
    sess = session_service.create_session(db, obj_in=obj_in)
    return APIResponse(
        success=True,
        message="Quiz session room launched successfully.",
        data=SessionResponse.model_validate(sess),
    )


@session_router.post(
    "/{id}/start",
    response_model=APIResponse[SessionResponse],
    status_code=status.HTTP_200_OK,
    summary="Start live session room",
    dependencies=[Depends(require_role(UserRole.TEACHER))],
)
async def start_session(id: UUID, db: Session = Depends(get_db)):
    """
    Move the session room to LIVE state (restricted to teachers).
    """
    sess = session_service.start_session(db, session_id=id)
    room_id_str = str(id)

    # Broadcast room status LIVE
    await connection_manager.broadcast_to_room(
        room_id_str,
        {
            "event": WebSocketEventType.ROOM_STATUS_CHANGED.value,
            "data": {"session_id": str(id), "status": sess.status.value},
        },
    )

    return APIResponse(
        success=True,
        message="Session is now live.",
        data=SessionResponse.model_validate(sess),
    )


@session_router.post(
    "/{id}/pause",
    response_model=APIResponse[SessionResponse],
    status_code=status.HTTP_200_OK,
    summary="Pause live session room",
    dependencies=[Depends(require_role(UserRole.TEACHER))],
)
async def pause_session(id: UUID, db: Session = Depends(get_db)):
    """
    Pause an ongoing session room, blocking new responses (restricted to teachers).
    """
    sess = session_service.pause_session(db, session_id=id)
    room_id_str = str(id)

    # Broadcast room status PAUSED
    await connection_manager.broadcast_to_room(
        room_id_str,
        {
            "event": WebSocketEventType.ROOM_STATUS_CHANGED.value,
            "data": {"session_id": str(id), "status": sess.status.value},
        },
    )

    return APIResponse(
        success=True,
        message="Session paused successfully.",
        data=SessionResponse.model_validate(sess),
    )


@session_router.post(
    "/{id}/resume",
    response_model=APIResponse[SessionResponse],
    status_code=status.HTTP_200_OK,
    summary="Resume paused session room",
    dependencies=[Depends(require_role(UserRole.TEACHER))],
)
async def resume_session(id: UUID, db: Session = Depends(get_db)):
    """
    Resume a paused session room (restricted to teachers).
    """
    sess = session_service.resume_session(db, session_id=id)
    room_id_str = str(id)

    # Broadcast room status LIVE
    await connection_manager.broadcast_to_room(
        room_id_str,
        {
            "event": WebSocketEventType.ROOM_STATUS_CHANGED.value,
            "data": {"session_id": str(id), "status": sess.status.value},
        },
    )

    return APIResponse(
        success=True,
        message="Session resumed, now live.",
        data=SessionResponse.model_validate(sess),
    )


@session_router.post(
    "/{id}/end",
    response_model=APIResponse[SessionResponse],
    status_code=status.HTTP_200_OK,
    summary="End live session room",
    dependencies=[Depends(require_role(UserRole.TEACHER))],
)
async def end_session(id: UUID, db: Session = Depends(get_db)):
    """
    Complete the session room, marking it as finished (restricted to teachers).
    """
    sess = session_service.end_session(db, session_id=id)
    room_id_str = str(id)

    # Broadcast room status COMPLETED / SESSION_FINISHED
    await connection_manager.broadcast_to_room(
        room_id_str,
        {
            "event": WebSocketEventType.ROOM_STATUS_CHANGED.value,
            "data": {"session_id": str(id), "status": sess.status.value},
        },
    )

    return APIResponse(
        success=True,
        message="Session ended and closed.",
        data=SessionResponse.model_validate(sess),
    )


@session_router.post(
    "/{id}/activate-question",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Set active session question",
    dependencies=[Depends(require_role(UserRole.TEACHER))],
)
async def activate_question(
    id: UUID, payload: ActivateQuestionRequest, db: Session = Depends(get_db)
):
    """
    Explicitly changes the active question displayed in the student panel (restricted to teachers).
    """
    q_id = session_service.activate_question(db, session_id=id, question_id=payload.question_id)
    question = question_service.get_question(db, question_id=q_id)
    room_id_str = str(id)

    # 1. Broadcast QUESTION_ACTIVATED
    await connection_manager.broadcast_to_room(
        room_id_str,
        {
            "event": WebSocketEventType.QUESTION_ACTIVATED.value,
            "data": {
                "question_id": str(q_id),
                "question_text": question.question_text,
                "question_type": question.question_type.value,
                "options": question.options,
                "time_limit_seconds": question.default_time_limit_seconds,
            },
        },
    )

    # 2. Broadcast COUNTDOWN_STARTED
    if question.default_time_limit_seconds:
        await connection_manager.broadcast_to_room(
            room_id_str,
            {
                "event": WebSocketEventType.COUNTDOWN_STARTED.value,
                "data": {
                    "question_id": str(q_id),
                    "duration_seconds": question.default_time_limit_seconds,
                },
            },
        )

    return APIResponse(
        success=True,
        message="Active question updated.",
        data={"active_question_id": q_id},
    )


@session_router.post(
    "/{id}/next-question",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Advance to next question",
    dependencies=[Depends(require_role(UserRole.TEACHER))],
)
async def next_question(id: UUID, db: Session = Depends(get_db)):
    """
    Advances the pointer to the next question in the quiz compilation order (restricted to teachers).
    """
    q_id = session_service.next_question(db, session_id=id)
    room_id_str = str(id)

    if q_id:
        question = question_service.get_question(db, question_id=q_id)

        # 1. Broadcast QUESTION_ACTIVATED
        await connection_manager.broadcast_to_room(
            room_id_str,
            {
                "event": WebSocketEventType.QUESTION_ACTIVATED.value,
                "data": {
                    "question_id": str(q_id),
                    "question_text": question.question_text,
                    "question_type": question.question_type.value,
                    "options": question.options,
                    "time_limit_seconds": question.default_time_limit_seconds,
                },
            },
        )

        # 2. Broadcast COUNTDOWN_STARTED
        if question.default_time_limit_seconds:
            await connection_manager.broadcast_to_room(
                room_id_str,
                {
                    "event": WebSocketEventType.COUNTDOWN_STARTED.value,
                    "data": {
                        "question_id": str(q_id),
                        "duration_seconds": question.default_time_limit_seconds,
                    },
                },
            )

    return APIResponse(
        success=True,
        message="Advanced to next question.",
        data={"active_question_id": q_id},
    )


@session_router.get(
    "/{id}/leaderboard",
    response_model=APIResponse[List[ParticipantResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get current leaderboard",
)
def get_leaderboard(id: UUID, db: Session = Depends(get_db)):
    """
    Get live session standings sorted by performance/score.
    """
    leaderboard = session_service.get_leaderboard(db, session_id=id)
    return APIResponse(
        success=True,
        message="Leaderboard standings retrieved.",
        data=[ParticipantResponse.model_validate(p) for p in leaderboard],
    )


@session_router.get(
    "/{id}/participants",
    response_model=APIResponse[List[ParticipantResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get current participants roster",
)
def get_participants(id: UUID, db: Session = Depends(get_db)):
    """
    List all students/participants registered in this session room.
    """
    participants = session_service.get_participants(db, session_id=id)
    return APIResponse(
        success=True,
        message="Participants list retrieved.",
        data=[ParticipantResponse.model_validate(p) for p in participants],
    )


@session_router.get(
    "/{id}/status",
    response_model=APIResponse[RoomStatusResponse],
    status_code=status.HTTP_200_OK,
    summary="Get room execution status",
)
def get_room_status(id: UUID, db: Session = Depends(get_db)):
    """
    Returns room status and active question info.
    """
    sess = session_service.get_session(db, session_id=id)
    active_q = session_service.get_active_question(db, session_id=id)
    data = RoomStatusResponse(
        session_id=sess.id,
        room_code=sess.room_code,
        status=sess.status,
        active_question_id=active_q,
    )
    return APIResponse(
        success=True,
        message="Room status retrieved successfully.",
        data=data,
    )


@session_router.get(
    "/{id}/questions",
    response_model=APIResponse[List[QuestionResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get all questions for a session",
)
def get_session_questions(id: UUID, db: Session = Depends(get_db)):
    """
    Retrieve all quiz questions associated with the session.
    """
    questions = session_service.get_session_questions(db, session_id=id)
    return APIResponse(
        success=True,
        message="Session questions retrieved successfully.",
        data=[QuestionResponse.model_validate(q) for q in questions],
    )
