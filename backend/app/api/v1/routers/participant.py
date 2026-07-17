from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List, Any, Dict
from decimal import Decimal
from pydantic import BaseModel, Field

from app.api.responses import APIResponse
from app.schemas.participant import ParticipantResponse
from app.schemas.response import ResponseResponse
from app.services.participant_service import participant_service
from app.services.session_service import session_service
from app.database.session import get_db
from app.api.v1.dependencies.auth import get_current_user
from app.models.user import User
from app.exceptions import BusinessRuleException, ResourceNotFoundException
from app.websockets import connection_manager
from app.websockets.events import WebSocketEventType

participant_router = APIRouter()


class JoinRoomRequest(BaseModel):
    room_code: str = Field(..., max_length=10, description="The unique code to join the room")


class SubmitAnswerRequest(BaseModel):
    question_id: UUID = Field(..., description="UUID of the question being answered")
    selected_answer: Dict[str, Any] = Field(..., description="Selected options/answers payload")
    response_time_ms: Optional[int] = Field(None, ge=0, description="Response time in milliseconds")


class ScoreStatsResponse(BaseModel):
    participant_id: UUID
    score: Decimal
    correct_answers: int
    wrong_answers: int
    total_time_ms: int


@participant_router.post(
    "/join",
    response_model=APIResponse[ParticipantResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Join a session room using room code",
)
async def join_room(
    payload: JoinRoomRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Registers the logged-in student inside a session room by matching its room code.
    """
    try:
        sess = session_service.get_session_by_room_code(db, room_code=payload.room_code)
    except ResourceNotFoundException:
        raise BusinessRuleException(
            "No active room matches the provided room code.", code="ROOM_NOT_FOUND"
        )

    part = participant_service.join_session(db, session_id=sess.id, user_id=current_user.id)
    room_id_str = str(sess.id)

    # 1. Broadcast PARTICIPANT_JOINED
    await connection_manager.broadcast_to_room(
        room_id_str,
        {
            "event": WebSocketEventType.PARTICIPANT_JOINED.value,
            "data": {
                "participant_id": str(part.id),
                "user_id": str(current_user.id),
                "name": current_user.name,
            },
        },
    )

    # 2. Broadcast updated leaderboard
    leaderboard = session_service.get_leaderboard(db, session_id=sess.id)
    await connection_manager.broadcast_to_room(
        room_id_str,
        {
            "event": WebSocketEventType.LEADERBOARD_UPDATED.value,
            "data": [
                {
                    "participant_id": str(p.id),
                    "name": p.user.name,
                    "score": float(p.score),
                    "correct_answers": p.correct_answers,
                    "wrong_answers": p.wrong_answers,
                    "total_time_ms": p.total_time_ms,
                }
                for p in leaderboard
            ],
        },
    )

    return APIResponse(
        success=True,
        message="Successfully joined the session room.",
        data=ParticipantResponse.model_validate(part),
    )


@participant_router.delete(
    "/{participant_id}/leave",
    response_model=APIResponse[ParticipantResponse],
    status_code=status.HTTP_200_OK,
    summary="Leave the session room",
)
async def leave_room(
    participant_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Unregisters the participant, removing their presence from the session room.
    """
    part = participant_service.get_participant(db, participant_id=participant_id)
    room_id_str = str(part.session_id)

    deleted_part = participant_service.leave_session(db, participant_id=participant_id)

    # 1. Broadcast PARTICIPANT_LEFT
    await connection_manager.broadcast_to_room(
        room_id_str,
        {
            "event": WebSocketEventType.PARTICIPANT_LEFT.value,
            "data": {
                "participant_id": str(part.id),
                "user_id": str(current_user.id),
                "name": current_user.name,
            },
        },
    )

    # 2. Broadcast updated leaderboard
    leaderboard = session_service.get_leaderboard(db, session_id=part.session_id)
    await connection_manager.broadcast_to_room(
        room_id_str,
        {
            "event": WebSocketEventType.LEADERBOARD_UPDATED.value,
            "data": [
                {
                    "participant_id": str(p.id),
                    "name": p.user.name,
                    "score": float(p.score),
                    "correct_answers": p.correct_answers,
                    "wrong_answers": p.wrong_answers,
                    "total_time_ms": p.total_time_ms,
                }
                for p in leaderboard
            ],
        },
    )

    return APIResponse(
        success=True,
        message="Successfully left the session room.",
        data=ParticipantResponse.model_validate(deleted_part),
    )


@participant_router.post(
    "/{participant_id}/answers",
    response_model=APIResponse[ResponseResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Submit answer to active question",
)
async def submit_answer(
    participant_id: UUID,
    payload: SubmitAnswerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submit a selection response for the specified question.
    """
    part = participant_service.get_participant(db, participant_id)
    session = session_service.get_session(db, session_id=part.session_id)
    
    from app.common.enums import DeliveryMode
    if session.delivery_mode == DeliveryMode.INTERACTIVE:
        active_q = session_service.get_active_question(db, session_id=part.session_id)
        if active_q != payload.question_id:
            raise BusinessRuleException(
                "Cannot submit answer. This question is not currently active.",
                code="QUESTION_NOT_ACTIVE",
            )

    resp = participant_service.submit_answer(
        db,
        participant_id=participant_id,
        question_id=payload.question_id,
        selected_answer=payload.selected_answer,
        response_time_ms=payload.response_time_ms,
    )
    room_id_str = str(part.session_id)

    # 1. Broadcast ANSWER_SUBMITTED
    await connection_manager.broadcast_to_room(
        room_id_str,
        {
            "event": WebSocketEventType.ANSWER_SUBMITTED.value,
            "data": {
                "participant_id": str(participant_id),
                "name": current_user.name,
                "question_id": str(payload.question_id),
            },
        },
    )

    # 2. Broadcast updated leaderboard
    leaderboard = session_service.get_leaderboard(db, session_id=part.session_id)
    await connection_manager.broadcast_to_room(
        room_id_str,
        {
            "event": WebSocketEventType.LEADERBOARD_UPDATED.value,
            "data": [
                {
                    "participant_id": str(p.id),
                    "name": p.user.name,
                    "score": float(p.score),
                    "correct_answers": p.correct_answers,
                    "wrong_answers": p.wrong_answers,
                    "total_time_ms": p.total_time_ms,
                }
                for p in leaderboard
            ],
        },
    )

    return APIResponse(
        success=True,
        message="Answer submitted successfully.",
        data=ResponseResponse.model_validate(resp),
    )


@participant_router.get(
    "/{participant_id}/score",
    response_model=APIResponse[ScoreStatsResponse],
    status_code=status.HTTP_200_OK,
    summary="Get current score and stats",
)
def get_current_score(
    participant_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieves the score standing and response correct/wrong counts.
    """
    part = participant_service.get_participant(db, participant_id=participant_id)
    stats = ScoreStatsResponse(
        participant_id=part.id,
        score=part.score,
        correct_answers=part.correct_answers,
        wrong_answers=part.wrong_answers,
        total_time_ms=part.total_time_ms,
    )
    return APIResponse(
        success=True,
        message="Participant score statistics retrieved.",
        data=stats,
    )


@participant_router.get(
    "/{participant_id}/history",
    response_model=APIResponse[List[ResponseResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get response history",
)
def get_answer_history(
    participant_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Lists the participant's past response answers.
    """
    history = participant_service.get_participant_responses(
        db, participant_id=participant_id
    )
    return APIResponse(
        success=True,
        message="Answer response history retrieved.",
        data=[ResponseResponse.model_validate(r) for r in history],
    )
