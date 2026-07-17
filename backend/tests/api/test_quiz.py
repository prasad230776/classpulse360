from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_api_quiz_crud(
    client: TestClient, db: Session, teacher_headers: dict, test_teacher
):
    payload = {
        "title": "Algebra Quiz 101",
        "description": "Basic algebraic variables test",
        "created_by": str(test_teacher.id),
        "visibility": "PUBLIC",
        "shuffle_questions": True,
        "shuffle_options": False,
        "allow_answer_change": True,
        "show_results_after_each_question": True,
    }
    response = client.post(
        "/api/v1/quizzes/", json=payload, headers=teacher_headers
    )
    assert response.status_code == 201
    quiz_id = response.json()["data"]["id"]

    # Get Quiz
    response = client.get(f"/api/v1/quizzes/{quiz_id}", headers=teacher_headers)
    assert response.status_code == 200
    assert response.json()["data"]["title"] == "Algebra Quiz 101"
