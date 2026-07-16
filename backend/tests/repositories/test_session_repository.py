import pytest
from sqlalchemy.orm import Session
from app.repositories.user_repository import user_repository
from app.repositories.quiz_repository import quiz_repository
from app.repositories.session_repository import session_repository

from app.schemas.user import UserCreate
from app.schemas.quiz import QuizCreate
from app.schemas.session import SessionCreate
from app.common.enums import DeliveryMode, SessionStatus


def test_create_and_query_sessions(db: Session):
    """
    Test session initialization, custom room code generation trigger, and active filters.
    """
    user = user_repository.create_user(db, obj_in=UserCreate(
        name="Host Teacher", username="hostteacher", email="host@example.com", password="password"
    ))
    quiz = quiz_repository.create(db, obj_in=QuizCreate(title="Trivia Quiz", created_by=user.id))

    # Room code is omitted so the PostgreSQL DB trigger fn_generate_room_code() generates it
    sess_in = SessionCreate(
        quiz_id=quiz.id,
        created_by=user.id,
        delivery_mode=DeliveryMode.INTERACTIVE,
        status=SessionStatus.LIVE
    )
    session = session_repository.create(db, obj_in=sess_in)
    assert session.id is not None
    # Verify that the DB trigger successfully ran and populated the room_code
    assert session.room_code is not None
    assert len(session.room_code) == 6

    # Get by room code
    fetched = session_repository.get_by_room_code(db, session.room_code)
    assert fetched is not None
    assert fetched.id == session.id

    # Get active sessions
    active_sessions = session_repository.get_active_sessions(db)
    assert any(s.id == session.id for s in active_sessions)
