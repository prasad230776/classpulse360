import pytest
from decimal import Decimal
from sqlalchemy.orm import Session
from app.repositories.subject_repository import subject_repository
from app.repositories.topic_repository import topic_repository
from app.repositories.user_repository import user_repository
from app.repositories.question_repository import question_repository
from app.repositories.quiz_repository import quiz_repository
from app.repositories.session_repository import session_repository
from app.repositories.participant_repository import participant_repository
from app.repositories.response_repository import response_repository

from app.schemas.subject import SubjectCreate
from app.schemas.topic import TopicCreate
from app.schemas.user import UserCreate
from app.schemas.question import QuestionCreate
from app.schemas.quiz import QuizCreate
from app.schemas.session import SessionCreate
from app.schemas.participant import ParticipantCreate
from app.schemas.response import ResponseCreate


def test_participant_response_tracking(db: Session):
    """
    Test recording a participant's answer to a specific question.
    """
    # Parent setup (Subject, Topic, User Creator, Question)
    subject = subject_repository.create(db, obj_in=SubjectCreate(name="Biology", code="BIO01"))
    topic = topic_repository.create(db, obj_in=TopicCreate(subject_id=subject.id, name="Genetics", code="GEN01"))
    teacher = user_repository.create_user(db, obj_in=UserCreate(
        name="Gregor Mendel", username="gregormendel", email="mendel@peas.com", password="peas_long_password"
    ))
    question = question_repository.create(db, obj_in=QuestionCreate(
        topic_id=topic.id,
        created_by=teacher.id,
        question_text="Are pea plant traits inherited?",
        options={},
        correct_answer={"yes": True}
    ))

    # Quiz & Session
    quiz = quiz_repository.create(db, obj_in=QuizCreate(title="Pea Genetics Quiz", created_by=teacher.id))
    session = session_repository.create(db, obj_in=SessionCreate(quiz_id=quiz.id, created_by=teacher.id))

    # Student Participant
    student = user_repository.create_user(db, obj_in=UserCreate(
        name="Student Mendel", username="studentmendel", email="student@peas.com", password="password"
    ))
    participant = participant_repository.create(db, obj_in=ParticipantCreate(session_id=session.id, user_id=student.id))

    # Submit Response
    resp_in = ResponseCreate(
        participant_id=participant.id,
        question_id=question.id,
        selected_answer={"yes": True},
        is_correct=True,
        score_awarded=Decimal("1.00"),
        response_time_ms=1200
    )
    response = response_repository.create(db, obj_in=resp_in)
    assert response.id is not None
    assert response.is_correct

    # Query responses
    responses = response_repository.get_by_participant(db, participant.id)
    assert len(responses) == 1
    assert responses[0].question_id == question.id

    # Retrieve individual answer association
    fetched = response_repository.get_response(db, participant.id, question.id)
    assert fetched is not None
    assert fetched.score_awarded == Decimal("1.00")
