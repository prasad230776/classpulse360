from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.quiz import Quiz
from app.models.session import Session as QuizSession
from app.core.security import create_access_token


def test_websocket_connection(client: TestClient, db: Session, test_teacher):
    # Seed Quiz
    quiz = Quiz(title="WS Quiz", created_by=test_teacher.id, is_active=True)
    db.add(quiz)
    db.commit()

    # Seed Session
    session = QuizSession(
        quiz_id=quiz.id,
        created_by=test_teacher.id,
        status="LIVE",
        room_code="WSROOM1",
    )
    db.add(session)
    db.commit()

    token = create_access_token(subject=test_teacher.id)

    # 1. Establish WebSocket handshake
    with client.websocket_connect(
        f"/ws/session/WSROOM1?token={token}"
    ) as websocket:
        # Handshake established successfully, socket closes cleanly at exit of context manager
        pass
