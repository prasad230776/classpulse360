import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from decimal import Decimal

from app.models.subject import Subject
from app.models.topic import Topic
from app.models.question import Question
from app.models.quiz import Quiz
from app.models.quiz_question import QuizQuestion
from app.models.session import Session as QuizSession
from app.common.enums import QuestionType, DeliveryMode, VisibilityType, DifficultyLevel


def test_assignment_and_non_interactive_flow(
    client: TestClient,
    db: Session,
    teacher_headers: dict,
    student_headers: dict,
    test_teacher,
    test_student,
):
    # 1. Create parent Subject & Topic
    subject = Subject(name="Computer Science", code="CS01")
    db.add(subject)
    db.commit()

    topic = Topic(subject_id=subject.id, name="Databases", code="DB01")
    db.add(topic)
    db.commit()

    # 2. Create questions of types URL, FILE, TEXT
    q_url = Question(
        topic_id=topic.id,
        created_by=test_teacher.id,
        visibility=VisibilityType.PUBLIC,
        question_text="Submit your project URL",
        question_type=QuestionType.URL,
        options={},
        correct_answer={},
        difficulty_level=DifficultyLevel.MEDIUM,
        default_marks=Decimal("5.00"),
        default_time_limit_seconds=300,
    )
    q_file = Question(
        topic_id=topic.id,
        created_by=test_teacher.id,
        visibility=VisibilityType.PUBLIC,
        question_text="Submit your report PDF",
        question_type=QuestionType.FILE,
        options={},
        correct_answer={},
        difficulty_level=DifficultyLevel.MEDIUM,
        default_marks=Decimal("10.00"),
        default_time_limit_seconds=300,
    )
    q_text = Question(
        topic_id=topic.id,
        created_by=test_teacher.id,
        visibility=VisibilityType.PUBLIC,
        question_text="Write an essay on SQL",
        question_type=QuestionType.TEXT,
        options={},
        correct_answer={},
        difficulty_level=DifficultyLevel.MEDIUM,
        default_marks=Decimal("15.00"),
        default_time_limit_seconds=300,
    )
    db.add_all([q_url, q_file, q_text])
    db.commit()

    # 3. Create Quiz and map questions
    quiz = Quiz(title="Database Assignment", created_by=test_teacher.id, is_active=True)
    db.add(quiz)
    db.commit()

    qq_url = QuizQuestion(quiz_id=quiz.id, question_id=q_url.id, question_order=1, marks=Decimal("5.00"))
    qq_file = QuizQuestion(quiz_id=quiz.id, question_id=q_file.id, question_order=2, marks=Decimal("10.00"))
    qq_text = QuizQuestion(quiz_id=quiz.id, question_id=q_text.id, question_order=3, marks=Decimal("15.00"))
    db.add_all([qq_url, qq_file, qq_text])
    db.commit()

    # 4. Create Session in ASSIGNMENT mode
    session = QuizSession(
        quiz_id=quiz.id,
        created_by=test_teacher.id,
        status="LIVE",
        room_code="ASSIGN1",
        delivery_mode=DeliveryMode.ASSIGNMENT,
    )
    db.add(session)
    db.commit()

    # 5. Student Joins the session
    join_payload = {"room_code": "ASSIGN1"}
    response = client.post("/api/v1/participants/join", json=join_payload, headers=student_headers)
    assert response.status_code == 201
    part_id = response.json()["data"]["id"]

    # 6. Student fetches all questions for the session
    response = client.get(f"/api/v1/sessions/{session.id}/questions", headers=student_headers)
    assert response.status_code == 200
    questions_list = response.json()["data"]
    assert len(questions_list) == 3

    # 7. Student submits URL assignment response
    answer_payload = {
        "question_id": str(q_url.id),
        "selected_answer": {"url": "https://github.com/prasad230776/classpulse360"},
        "response_time_ms": 5000,
    }
    response = client.post(f"/api/v1/participants/{part_id}/answers", json=answer_payload, headers=student_headers)
    assert response.status_code == 201
    assert response.json()["data"]["is_correct"] is None
    assert float(response.json()["data"]["score_awarded"]) == 0.0

    # 8. Student submits FILE assignment response
    answer_payload = {
        "question_id": str(q_file.id),
        "selected_answer": {"file_url": "https://supabase.com/storage/v1/object/public/reports/123.pdf"},
        "response_time_ms": 8000,
    }
    response = client.post(f"/api/v1/participants/{part_id}/answers", json=answer_payload, headers=student_headers)
    assert response.status_code == 201
    assert response.json()["data"]["is_correct"] is None

    # 9. Student submits TEXT assignment response
    answer_payload = {
        "question_id": str(q_text.id),
        "selected_answer": {"text": "SQL is a domain-specific language used in programming..."},
        "response_time_ms": 12000,
    }
    response = client.post(f"/api/v1/participants/{part_id}/answers", json=answer_payload, headers=student_headers)
    assert response.status_code == 201
    assert response.json()["data"]["is_correct"] is None

    # 10. Student submits invalid URL format (fails validation)
    answer_payload = {
        "question_id": str(q_url.id),
        "selected_answer": {"url": "invalid-url-format"},
    }
    response = client.post(f"/api/v1/participants/{part_id}/answers", json=answer_payload, headers=student_headers)
    assert response.status_code == 400
    assert response.json()["metadata"]["code"] == "INVALID_SUBMISSION"
