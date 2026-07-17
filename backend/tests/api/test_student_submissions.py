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


def test_student_submissions_endpoints(
    client: TestClient,
    db: Session,
    teacher_headers: dict,
    student_headers: dict,
    test_teacher,
    test_student,
):
    # 1. Create parent Subject & Topic
    subject = Subject(name="Computer Networks", code="CS04")
    db.add(subject)
    db.commit()

    topic = Topic(subject_id=subject.id, name="IP Routing", code="IP01")
    db.add(topic)
    db.commit()

    # 2. Create question
    question = Question(
        topic_id=topic.id,
        created_by=test_teacher.id,
        visibility=VisibilityType.PUBLIC,
        question_text="Explain CIDR notation.",
        question_type=QuestionType.TEXT,
        options={},
        correct_answer={},
        difficulty_level=DifficultyLevel.EASY,
        default_marks=Decimal("5.00"),
        default_time_limit_seconds=180,
    )
    db.add(question)
    db.commit()

    # 3. Create Quiz
    quiz = Quiz(title="Networks CIDR Assignment", created_by=test_teacher.id, is_active=True)
    db.add(quiz)
    db.commit()

    qq = QuizQuestion(quiz_id=quiz.id, question_id=question.id, question_order=1, marks=Decimal("5.00"))
    db.add(qq)
    db.commit()

    # 4. Create Session in ASSIGNMENT mode
    session = QuizSession(
        quiz_id=quiz.id,
        created_by=test_teacher.id,
        status="LIVE",
        room_code="NETIP",
        delivery_mode=DeliveryMode.ASSIGNMENT,
    )
    db.add(session)
    db.commit()

    # 5. Student Joins the session
    join_payload = {"room_code": "NETIP"}
    response = client.post("/api/v1/participants/join", json=join_payload, headers=student_headers)
    assert response.status_code == 201
    part_id = response.json()["data"]["id"]

    # 6. Student submits TEXT assignment response
    answer_payload = {
        "question_id": str(question.id),
        "selected_answer": {"text": "CIDR stands for Classless Inter-Domain Routing."},
        "response_time_ms": 15000,
        "submission_status": "SUBMITTED"
    }
    response = client.post(f"/api/v1/participants/{part_id}/answers", json=answer_payload, headers=student_headers)
    assert response.status_code == 201
    submission_id = response.json()["data"]["id"]

    # 7. Student lists all of their own submissions
    response = client.get("/api/v1/quizzes/student/submissions", headers=student_headers)
    assert response.status_code == 200
    submissions_list = response.json()["data"]
    assert len(submissions_list) >= 1
    # Check that our submission_id is in the returned list
    retrieved_ids = [s["id"] for s in submissions_list]
    assert submission_id in retrieved_ids

    # 8. Student gets details of their single submission
    response = client.get(f"/api/v1/quizzes/student/submissions/{submission_id}", headers=student_headers)
    assert response.status_code == 200
    assert response.json()["data"]["id"] == submission_id
    assert response.json()["data"]["selected_answer"]["text"] == "CIDR stands for Classless Inter-Domain Routing."

    # 9. Register a second student to try to view the first student's submission (should fail)
    # We can use headers without registration, but since auth is mocked/managed, let's register a new student user
    register_payload = {
        "email": "student2@example.com",
        "username": "student2",
        "password": "securepassword",
        "name": "Second Student",
        "role": "STUDENT",
    }
    client.post("/api/v1/auth/register", json=register_payload)
    
    login_payload = {
        "username": "student2@example.com",
        "password": "securepassword",
    }
    login_response = client.post("/api/v1/auth/login", data=login_payload)
    token = login_response.json()["data"]["access_token"]
    student2_headers = {"Authorization": f"Bearer {token}"}

    # Student 2 attempts to fetch Student 1's submission (should return 404 Not Found)
    response = client.get(f"/api/v1/quizzes/student/submissions/{submission_id}", headers=student2_headers)
    assert response.status_code == 404
