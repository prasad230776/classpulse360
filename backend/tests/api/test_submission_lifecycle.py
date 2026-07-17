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


def test_submission_lifecycle_flow(
    client: TestClient,
    db: Session,
    teacher_headers: dict,
    student_headers: dict,
    test_teacher,
    test_student,
):
    # 1. Create parent Subject & Topic
    subject = Subject(name="Operating Systems", code="CS03")
    db.add(subject)
    db.commit()

    topic = Topic(subject_id=subject.id, name="Processes", code="PROC01")
    db.add(topic)
    db.commit()

    # 2. Create question of type TEXT
    question = Question(
        topic_id=topic.id,
        created_by=test_teacher.id,
        visibility=VisibilityType.PUBLIC,
        question_text="Describe process state transitions.",
        question_type=QuestionType.TEXT,
        options={},
        correct_answer={},
        difficulty_level=DifficultyLevel.MEDIUM,
        default_marks=Decimal("10.00"),
        default_time_limit_seconds=300,
    )
    db.add(question)
    db.commit()

    # 3. Create Quiz (resubmission/multiple attempts is disabled by default)
    quiz = Quiz(
        title="OS Process Quiz",
        created_by=test_teacher.id,
        is_active=True,
        settings_config={"allow_multiple_attempts": False}
    )
    db.add(quiz)
    db.commit()

    qq = QuizQuestion(quiz_id=quiz.id, question_id=question.id, question_order=1, marks=Decimal("10.00"))
    db.add(qq)
    db.commit()

    # 4. Create Session in ASSIGNMENT mode
    session = QuizSession(
        quiz_id=quiz.id,
        created_by=test_teacher.id,
        status="LIVE",
        room_code="OSLIFE",
        delivery_mode=DeliveryMode.ASSIGNMENT,
    )
    db.add(session)
    db.commit()

    # 5. Student Joins the session
    join_payload = {"room_code": "OSLIFE"}
    response = client.post("/api/v1/participants/join", json=join_payload, headers=student_headers)
    assert response.status_code == 201
    part_id = response.json()["data"]["id"]

    # 6. Student saves draft
    answer_payload = {
        "question_id": str(question.id),
        "selected_answer": {"text": "A process can transit from New to Ready..."},
        "response_time_ms": 10000,
        "submission_status": "DRAFT"
    }
    response = client.post(f"/api/v1/participants/{part_id}/answers", json=answer_payload, headers=student_headers)
    assert response.status_code == 201
    assert response.json()["data"]["submission_status"] == "DRAFT"

    # 7. Teacher attempts to grade the draft submission (should fail)
    grade_payload = {
        "score_awarded": 8.00,
        "feedback": "Cannot grade drafts.",
        "is_correct": True
    }
    response = client.put(
        f"/api/v1/participants/{part_id}/answers/{question.id}/grade",
        json=grade_payload,
        headers=teacher_headers
    )
    assert response.status_code == 400
    assert "Drafts cannot be graded" in response.json()["message"]

    # 8. Student submits the draft
    submit_payload = {
        "question_id": str(question.id),
        "selected_answer": {"text": "A process transit from New to Ready, and then Running when dispatched."},
        "response_time_ms": 20000,
        "submission_status": "SUBMITTED"
    }
    response = client.post(f"/api/v1/participants/{part_id}/answers", json=submit_payload, headers=student_headers)
    assert response.status_code == 201
    assert response.json()["data"]["submission_status"] == "SUBMITTED"

    # 9. Student attempts to modify the submitted response (should fail because resubmission is disabled)
    modify_payload = {
        "question_id": str(question.id),
        "selected_answer": {"text": "Late modification attempt."},
        "response_time_ms": 5000,
        "submission_status": "SUBMITTED"
    }
    response = client.post(f"/api/v1/participants/{part_id}/answers", json=modify_payload, headers=student_headers)
    assert response.status_code == 400
    assert "Submitted assignments cannot be modified" in response.json()["message"]

    # 10. Teacher grades the submitted response (should succeed)
    response = client.put(
        f"/api/v1/participants/{part_id}/answers/{question.id}/grade",
        json=grade_payload,
        headers=teacher_headers
    )
    assert response.status_code == 200
    assert response.json()["data"]["submission_status"] == "GRADED"
    assert float(response.json()["data"]["score_awarded"]) == 8.00
