from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.user import User


def test_api_register_and_login(client: TestClient, db: Session):
    # Test Register
    payload = {
        "name": "Jane Doe",
        "username": "janedoe",
        "email": "jane@example.com",
        "password": "securepassword123",
        "role": "STUDENT",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["success"] is True
    assert res_data["data"]["username"] == "janedoe"

    # Test Login
    login_payload = {"username": "jane@example.com", "password": "securepassword123"}
    response = client.post("/api/v1/auth/login", data=login_payload)
    assert response.status_code == 200
    res_data = response.json()
    assert "access_token" in res_data["data"]
    assert "refresh_token" in res_data["data"]


def test_api_me_profile(client: TestClient, student_headers: dict, test_student: User):
    response = client.get("/api/v1/auth/me", headers=student_headers)
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["data"]["email"] == test_student.email
