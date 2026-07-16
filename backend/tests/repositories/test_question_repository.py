import pytest
from sqlalchemy.orm import Session
from decimal import Decimal
from app.repositories.subject_repository import subject_repository
from app.repositories.topic_repository import topic_repository
from app.repositories.user_repository import user_repository
from app.repositories.question_repository import question_repository

from app.schemas.subject import SubjectCreate
from app.schemas.topic import TopicCreate
from app.schemas.user import UserCreate
from app.schemas.question import QuestionCreate
from app.common.enums import VisibilityType, QuestionType, DifficultyLevel


def test_create_and_query_questions(db: Session):
    """
    Test creating, fetching, and searching questions.
    """
    # Parent Subject & Topic
    subject = subject_repository.create(db, obj_in=SubjectCreate(name="Physics", code="PHYS01"))
    topic = topic_repository.create(db, obj_in=TopicCreate(subject_id=subject.id, name="Mechanics", code="MECH01"))

    # User Creator
    user = user_repository.create_user(db, obj_in=UserCreate(
        name="Dr. Newton", username="isaacnewton", email="newton@gravity.com", password="apple_long_password"
    ))

    # Questions
    q_in1 = QuestionCreate(
        topic_id=topic.id,
        created_by=user.id,
        visibility=VisibilityType.PUBLIC,
        question_text="What is Newton's First Law?",
        question_type=QuestionType.SHORT_ANSWER,
        options={},
        correct_answer={"text": "Inertia"},
        difficulty_level=DifficultyLevel.EASY,
        default_marks=Decimal("1.50")
    )
    q_in2 = QuestionCreate(
        topic_id=topic.id,
        created_by=user.id,
        visibility=VisibilityType.PRIVATE,
        question_text="Derive terminal velocity formula.",
        question_type=QuestionType.SHORT_ANSWER,
        options={},
        correct_answer={"formula": "v = sqrt(...)"},
        difficulty_level=DifficultyLevel.HARD,
        default_marks=Decimal("5.00")
    )

    q1 = question_repository.create(db, obj_in=q_in1)
    q2 = question_repository.create(db, obj_in=q_in2)

    assert q1.id is not None
    assert q2.id is not None

    # Get by topic
    questions = question_repository.get_by_topic(db, topic.id)
    assert len(questions) == 2

    # Search questions
    search_results = question_repository.search(db, "Newton's First")
    assert len(search_results) == 1
    assert search_results[0].id == q1.id
