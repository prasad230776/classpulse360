import pytest
from sqlalchemy.orm import Session
from app.repositories.user_repository import user_repository
from app.repositories.quiz_repository import quiz_repository

from app.schemas.user import UserCreate
from app.schemas.quiz import QuizCreate
from app.common.enums import VisibilityType


def test_create_and_query_quizzes(db: Session):
    """
    Test creating a quiz template and fetching it by teacher or visibility.
    """
    teacher = user_repository.create_user(db, obj_in=UserCreate(
        name="Prof. Einstein", username="alberteinstein", email="einstein@relativity.com", password="speedoflight"
    ))

    quiz_in1 = QuizCreate(
        title="General Relativity Basics",
        description="Introduction to spacetime curvature.",
        visibility=VisibilityType.PUBLIC,
        created_by=teacher.id
    )
    quiz_in2 = QuizCreate(
        title="Quantum Mechanics Advanced",
        description="Private draft of QM questions.",
        visibility=VisibilityType.PRIVATE,
        created_by=teacher.id
    )

    q1 = quiz_repository.create(db, obj_in=quiz_in1)
    q2 = quiz_repository.create(db, obj_in=quiz_in2)

    assert q1.id is not None
    assert q2.id is not None

    # Get by teacher
    teacher_quizzes = quiz_repository.get_by_teacher(db, teacher.id)
    assert len(teacher_quizzes) == 2

    # Get published quizzes
    published = quiz_repository.get_published_quizzes(db)
    assert any(q.id == q1.id for q in published)
    assert not any(q.id == q2.id for q in published)
