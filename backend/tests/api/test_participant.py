from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.quiz import Quiz
from app.models.session import Session as QuizSession


def test_api_participant_flow(
    client: TestClient,
    db: Session,
    teacher_headers: dict,
    student_headers: dict,
    test_teacher,
    test_student,
):
    # Seed parent Quiz
    quiz = Quiz(title="Maths Quiz", created_by=test_teacher.id, is_active=True)
    db.add(quiz)
    db.commit()

    # Seed Session room
    session = QuizSession(
        quiz_id=quiz.id,
        created_by=test_teacher.id,
        status="LIVE",
        room_code="CODE123",
    )
    db.add(session)
    db.commit()

    # 1. Join Room (By student)
    payload = {"room_code": "CODE123"}
    response = client.post(
        "/api/v1/participants/join", json=payload, headers=student_headers
    )
    assert response.status_code == 201
    part_id = response.json()["data"]["id"]

    # 2. Check Score stats
    response = client.get(
        f"/api/v1/participants/{part_id}/score", headers=student_headers
    )
    assert response.status_code == 200
    assert float(response.json()["data"]["score"]) == 0.0
