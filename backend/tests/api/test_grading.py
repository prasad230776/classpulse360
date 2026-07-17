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


def test_manual_grading_flow(
    client: TestClient,
    db: Session,
    teacher_headers: dict,
    student_headers: dict,
    test_teacher,
    test_student,
):
    # 1. Create parent Subject & Topic
    subject = Subject(name="Database Design", code="CS02")
    db.add(subject)
    db.commit()

    topic = Topic(subject_id=subject.id, name="Normalization", code="NORM01")
    db.add(topic)
    db.commit()

    # 2. Create question of type TEXT
    question = Question(
        topic_id=topic.id,
        created_by=test_teacher.id,
        visibility=VisibilityType.PUBLIC,
        question_text="Explain 3NF with an example.",
        question_type=QuestionType.TEXT,
        options={},
        correct_answer={},
        difficulty_level=DifficultyLevel.HARD,
        default_marks=Decimal("20.00"),
        default_time_limit_seconds=600,
    )
    db.add(question)
    db.commit()

    # 3. Create Quiz and map question
    quiz = Quiz(title="Database Normalization Test", created_by=test_teacher.id, is_active=True)
    db.add(quiz)
    db.commit()

    qq = QuizQuestion(quiz_id=quiz.id, question_id=question.id, question_order=1, marks=Decimal("20.00"))
    db.add(qq)
    db.commit()

    # 4. Create Session in ASSIGNMENT mode
    session = QuizSession(
        quiz_id=quiz.id,
        created_by=test_teacher.id,
        status="LIVE",
        room_code="GRADEME",
        delivery_mode=DeliveryMode.ASSIGNMENT,
    )
    db.add(session)
    db.commit()

    # 5. Student Joins the session
    join_payload = {"room_code": "GRADEME"}
    response = client.post("/api/v1/participants/join", json=join_payload, headers=student_headers)
    assert response.status_code == 201
    part_id = response.json()["data"]["id"]

    # 6. Student submits TEXT assignment response
    answer_payload = {
        "question_id": str(question.id),
        "selected_answer": {"text": "A table is in 3NF if it is in 2NF and has no transitive dependencies."},
        "response_time_ms": 30000,
    }
    response = client.post(f"/api/v1/participants/{part_id}/answers", json=answer_payload, headers=student_headers)
    assert response.status_code == 201
    assert response.json()["data"]["grading_status"] == "PENDING"
    assert response.json()["data"]["feedback"] is None
    assert float(response.json()["data"]["score_awarded"]) == 0.0

    # 7. Teacher grades student's submission (assigns marks + feedback)
    grade_payload = {
        "score_awarded": 18.50,
        "feedback": "Perfect description! Good example.",
        "is_correct": True
    }
    response = client.put(
        f"/api/v1/participants/{part_id}/answers/{question.id}/grade",
        json=grade_payload,
        headers=teacher_headers
    )
    assert response.status_code == 200
    assert response.json()["data"]["grading_status"] == "GRADED"
    assert response.json()["data"]["feedback"] == "Perfect description! Good example."
    assert float(response.json()["data"]["score_awarded"]) == 18.50
    assert response.json()["data"]["is_correct"] is True

    # 8. Student checks stats & verifies they see updated score
    response = client.get(f"/api/v1/participants/{part_id}/score", headers=student_headers)
    assert response.status_code == 200
    assert float(response.json()["data"]["score"]) == 18.50

    # 9. Teacher updates marks and feedback (re-grading)
    regrade_payload = {
        "score_awarded": 15.00,
        "feedback": "Re-graded. Marks adjusted.",
        "is_correct": True
    }
    response = client.put(
        f"/api/v1/participants/{part_id}/answers/{question.id}/grade",
        json=regrade_payload,
        headers=teacher_headers
    )
    assert response.status_code == 200
    assert float(response.json()["data"]["score_awarded"]) == 15.00

    # 10. Student checks stats and verifies score is adjusted
    response = client.get(f"/api/v1/participants/{part_id}/score", headers=student_headers)
    assert response.status_code == 200
    assert float(response.json()["data"]["score"]) == 15.00
