import pytest
from decimal import Decimal
from sqlalchemy.orm import Session
from app.repositories.subject_repository import subject_repository
from app.repositories.topic_repository import topic_repository
from app.repositories.user_repository import user_repository
from app.repositories.question_repository import question_repository
from app.repositories.quiz_repository import quiz_repository
from app.repositories.quiz_question_repository import quiz_question_repository

from app.schemas.subject import SubjectCreate
from app.schemas.topic import TopicCreate
from app.schemas.user import UserCreate
from app.schemas.question import QuestionCreate
from app.schemas.quiz import QuizCreate
from app.schemas.quiz_question import QuizQuestionCreate


def test_quiz_question_association(db: Session):
    """
    Test linking questions to quizzes and verifying order.
    """
    # Parent Subject & Topic
    subject = subject_repository.create(db, obj_in=SubjectCreate(name="Chemistry", code="CHEM01"))
    topic = topic_repository.create(db, obj_in=TopicCreate(subject_id=subject.id, name="Organic", code="ORG01"))

    # User Creator
    user = user_repository.create_user(db, obj_in=UserCreate(
        name="Marie Curie", username="mariecurie", email="curie@radiation.com", password="polonium"
    ))

    # Quiz
    quiz = quiz_repository.create(db, obj_in=QuizCreate(title="Radiation Quiz", created_by=user.id))

    # Question
    question = question_repository.create(db, obj_in=QuestionCreate(
        topic_id=topic.id,
        created_by=user.id,
        question_text="What is half life of Carbon-14?",
        options={},
        correct_answer={"years": 5730}
    ))

    # Associate
    assoc_in = QuizQuestionCreate(
        quiz_id=quiz.id,
        question_id=question.id,
        question_order=1,
        marks=Decimal("2.00")
    )
    association = quiz_question_repository.create(db, obj_in=assoc_in)
    assert association.id is not None

    # Retrieve ordered associations
    associations = quiz_question_repository.get_questions_by_quiz_id(db, quiz.id)
    assert len(associations) == 1
    assert associations[0].question_id == question.id

    # Retrieve specific association
    fetched = quiz_question_repository.get_association(db, quiz.id, question.id)
    assert fetched is not None
    assert fetched.marks == Decimal("2.00")
