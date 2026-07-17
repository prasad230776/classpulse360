import pytest
import io
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


def test_file_upload_validation_and_signed_url(
    client: TestClient,
    db: Session,
    teacher_headers: dict,
    student_headers: dict,
    test_teacher,
    test_student,
):
    # 1. Create parent Subject & Topic
    subject = Subject(name="Database Systems", code="CS06")
    db.add(subject)
    db.commit()

    topic = Topic(subject_id=subject.id, name="Indexing", code="IDX01")
    db.add(topic)
    db.commit()

    # 2. Create question of type FILE
    question = Question(
        topic_id=topic.id,
        created_by=test_teacher.id,
        visibility=VisibilityType.PUBLIC,
        question_text="Upload your indexing assignment report.",
        question_type=QuestionType.FILE,
        options={},
        correct_answer={},
        difficulty_level=DifficultyLevel.MEDIUM,
        default_marks=Decimal("15.00"),
        default_time_limit_seconds=600,
    )
    db.add(question)
    db.commit()

    # 3. Create Quiz with file settings (max file size 100 bytes, allowed extensions: .pdf, .txt)
    quiz = Quiz(
        title="Indexing Assignment",
        created_by=test_teacher.id,
        is_active=True,
        settings_config={
            "assignment_max_file_size": 100,
            "allowed_file_extensions": ["pdf", "txt"],
            "allowed_submission_types": ["FILE"]
        }
    )
    db.add(quiz)
    db.commit()

    qq = QuizQuestion(quiz_id=quiz.id, question_id=question.id, question_order=1, marks=Decimal("15.00"))
    db.add(qq)
    db.commit()

    # 4. Create Session in ASSIGNMENT mode
    session = QuizSession(
        quiz_id=quiz.id,
        created_by=test_teacher.id,
        status="LIVE",
        room_code="INDEX",
        delivery_mode=DeliveryMode.ASSIGNMENT,
    )
    db.add(session)
    db.commit()

    # 5. Student Joins the session
    join_payload = {"room_code": "INDEX"}
    response = client.post("/api/v1/participants/join", json=join_payload, headers=student_headers)
    assert response.status_code == 201
    part_id = response.json()["data"]["id"]

    # 6. Student submits a URL from an unsupported host
    response = client.post(
        f"/api/v1/participants/{part_id}/answers/{question.id}/upload",
        json={"file_url": "https://example.com/report.pdf"},
        headers=student_headers,
    )
    assert response.status_code == 400
    assert "Only URLs from GitHub, LinkedIn, or Google Drive" in response.json()["message"]

    # 7. Student submits a valid GitHub URL
    response = client.post(
        f"/api/v1/participants/{part_id}/answers/{question.id}/upload",
        json={"file_url": "https://github.com/org/repo/blob/main/report.pdf"},
        headers=student_headers,
    )
    assert response.status_code == 200
    resp_data = response.json()["data"]
    assert resp_data["selected_answer"]["file_url"] == "https://github.com/org/repo/blob/main/report.pdf"
    assert resp_data["selected_answer"]["source"] == "github"
