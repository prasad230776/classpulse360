import pytest
from decimal import Decimal
from sqlalchemy.orm import Session
from app.repositories.user_repository import user_repository
from app.repositories.quiz_repository import quiz_repository
from app.repositories.session_repository import session_repository
from app.repositories.participant_repository import participant_repository

from app.schemas.user import UserCreate
from app.schemas.quiz import QuizCreate
from app.schemas.session import SessionCreate
from app.schemas.participant import ParticipantCreate
from app.common.enums import ParticipantStatus


def test_participant_registration_and_leaderboard(db: Session):
    """
    Test adding participants to a session and retrieving them ranked by score.
    """
    teacher = user_repository.create_user(db, obj_in=UserCreate(
        name="Leaderboard Teacher", username="leadteacher", email="lead@example.com", password="password"
    ))
    quiz = quiz_repository.create(db, obj_in=QuizCreate(title="Competition Quiz", created_by=teacher.id))
    session = session_repository.create(db, obj_in=SessionCreate(quiz_id=quiz.id, created_by=teacher.id))

    student1 = user_repository.create_user(db, obj_in=UserCreate(
        name="Student One", username="studentone", email="one@student.com", password="password"
    ))
    student2 = user_repository.create_user(db, obj_in=UserCreate(
        name="Student Two", username="studenttwo", email="two@student.com", password="password"
    ))

    # Add participants
    p1 = participant_repository.create(db, obj_in=ParticipantCreate(session_id=session.id, user_id=student1.id))
    p2 = participant_repository.create(db, obj_in=ParticipantCreate(session_id=session.id, user_id=student2.id))

    assert p1.id is not None
    assert p2.id is not None

    # Update scores
    participant_repository.update(db, db_obj=p1, obj_in={"score": Decimal("85.00"), "correct_answers": 8})
    participant_repository.update(db, db_obj=p2, obj_in={"score": Decimal("95.00"), "correct_answers": 9})

    # Fetch leaderboard (by session ordered by score desc)
    leaderboard = participant_repository.get_by_session(db, session.id)
    assert len(leaderboard) == 2
    # student2 (95 points) should rank before student1 (85 points)
    assert leaderboard[0].user_id == student2.id
    assert leaderboard[1].user_id == student1.id

    # Fetch individual participant association
    association = participant_repository.get_participant(db, session.id, student1.id)
    assert association is not None
    assert association.id == p1.id
