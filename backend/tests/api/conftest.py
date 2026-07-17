import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from uuid import uuid4

from app.main import app
from app.database.session import get_db
from app.core.security import create_access_token, get_password_hash
from app.common.enums import UserRole, UserStatus
from app.models.user import User


@pytest.fixture(scope="function")
def client(db: Session, monkeypatch):
    """
    FastAPI TestClient fixture that overrides the database dependency injection
    to route queries inside the isolated test transaction block.
    """

    def _override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    # Monkeypatch SessionLocal to reuse the test transaction session in the WebSocket handler
    monkeypatch.setattr("app.websockets.session_socket.SessionLocal", lambda: db)

    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_teacher(db: Session) -> User:
    """
    Seeds a mock teacher profile in the database.
    """
    teacher = User(
        id=uuid4(),
        name="Test Teacher",
        username="testteacher",
        email="teacher@example.com",
        hashed_password=get_password_hash("password123"),
        role=UserRole.TEACHER,
        status=UserStatus.APPROVED,
        is_active=True,
    )
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return teacher


@pytest.fixture(scope="function")
def test_student(db: Session) -> User:
    """
    Seeds a mock student profile in the database.
    """
    student = User(
        id=uuid4(),
        name="Test Student",
        username="teststudent",
        email="student@example.com",
        hashed_password=get_password_hash("password123"),
        role=UserRole.STUDENT,
        status=UserStatus.APPROVED,
        is_active=True,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@pytest.fixture(scope="function")
def test_admin(db: Session) -> User:
    """
    Seeds a mock admin profile in the database.
    """
    admin = User(
        id=uuid4(),
        name="Test Admin",
        username="testadmin",
        email="admin@example.com",
        hashed_password=get_password_hash("password123"),
        role=UserRole.ADMIN,
        status=UserStatus.APPROVED,
        is_active=True,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@pytest.fixture(scope="function")
def teacher_headers(test_teacher: User):
    """
    Returns signed Bearer token headers for the seeded teacher user.
    """
    token = create_access_token(subject=test_teacher.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def student_headers(test_student: User):
    """
    Returns signed Bearer token headers for the seeded student user.
    """
    token = create_access_token(subject=test_student.id)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def admin_headers(test_admin: User):
    """
    Returns signed Bearer token headers for the seeded admin user.
    """
    token = create_access_token(subject=test_admin.id)
    return {"Authorization": f"Bearer {token}"}
