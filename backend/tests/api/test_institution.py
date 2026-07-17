from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_api_institution_crud(
    client: TestClient, admin_headers: dict, student_headers: dict
):
    # 1. Create (ADMIN role limit check)
    payload = {"name": "ClassPulse High", "code": "TESTCPH01", "institution_type": "SCHOOL"}
    # Reject student client
    response = client.post(
        "/api/v1/institutions/", json=payload, headers=student_headers
    )
    assert response.status_code == 403

    # Accept admin client
    response = client.post(
        "/api/v1/institutions/", json=payload, headers=admin_headers
    )
    assert response.status_code == 201
    inst_id = response.json()["data"]["id"]

    # 2. List (Accessible to any logged-in role)
    response = client.get("/api/v1/institutions/", headers=student_headers)
    assert response.status_code == 200
    assert len(response.json()["data"]) >= 1

    # 3. Read
    response = client.get(f"/api/v1/institutions/{inst_id}", headers=student_headers)
    assert response.status_code == 200
    assert response.json()["data"]["code"] == "TESTCPH01"
