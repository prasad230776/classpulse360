from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.subject import Subject
from app.models.topic import Topic


def test_api_question_crud(
    client: TestClient, db: Session, teacher_headers: dict, test_teacher
):
    # Seed parent subject and topic
    subject = Subject(name="Maths", code="MTH01")
    db.add(subject)
    db.commit()

    topic = Topic(name="Algebra", code="ALG01", subject_id=subject.id)
    db.add(topic)
    db.commit()

    # 1. Create Question
    payload = {
        "topic_id": str(topic.id),
        "created_by": str(test_teacher.id),
        "question_text": "What is x if x + 2 = 5?",
        "question_type": "MCQ_SINGLE",
        "options": {"choices": [{"id": "a", "text": "2"}, {"id": "b", "text": "3"}]},
        "correct_answer": {"id": "b"},
        "difficulty_level": "EASY",
        "default_marks": "1.00",
        "default_time_limit_seconds": 30,
    }
    response = client.post(
        "/api/v1/questions/", json=payload, headers=teacher_headers
    )
    assert response.status_code == 201
    q_id = response.json()["data"]["id"]

    # 2. Get Question
    response = client.get(f"/api/v1/questions/{q_id}", headers=teacher_headers)
    assert response.status_code == 200
    assert response.json()["data"]["question_text"] == "What is x if x + 2 = 5?"
