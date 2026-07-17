from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.quiz import Quiz


def test_api_session_lifecycle(
    client: TestClient, db: Session, teacher_headers: dict, test_teacher
):
    # Seed a quiz shell
    quiz = Quiz(title="Sample Quiz", created_by=test_teacher.id, is_active=True)
    db.add(quiz)
    db.commit()

    # 1. Create Session
    payload = {
        "quiz_id": str(quiz.id),
        "created_by": str(test_teacher.id),
        "delivery_mode": "INTERACTIVE",
    }
    response = client.post(
        "/api/v1/sessions/", json=payload, headers=teacher_headers
    )
    assert response.status_code == 201
    sess_id = response.json()["data"]["id"]

    # 2. Start Session
    response = client.post(
        f"/api/v1/sessions/{sess_id}/start", headers=teacher_headers
    )
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "LIVE"
