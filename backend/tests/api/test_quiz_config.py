import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.quiz import Quiz


def test_quiz_config_defaults_and_validation(
    client: TestClient,
    db: Session,
    teacher_headers: dict,
    test_teacher,
):
    # 1. Create Quiz with no settings_config passed (should fall back to defaults)
    payload = {
        "title": "Quiz Default Config",
        "description": "testing defaults",
        "created_by": str(test_teacher.id),
        "visibility": "PRIVATE",
    }
    response = client.post("/api/v1/quizzes/", json=payload, headers=teacher_headers)
    assert response.status_code == 201
    
    quiz_data = response.json()["data"]
    settings = quiz_data["settings_config"]
    
    # Assert sensible defaults
    assert settings["timer_duration"] is None
    assert settings["allow_multiple_attempts"] is False
    assert settings["show_results_immediately"] is True
    assert settings["show_correct_answers"] is True
    assert settings["require_fullscreen"] is False
    assert settings["allow_question_navigation"] is True
    assert settings["allowed_file_extensions"] == []
    
    quiz_id = quiz_data["id"]

    # 2. Update Quiz with custom settings
    update_payload = {
        "settings_config": {
            "timer_duration": 120,
            "allow_multiple_attempts": True,
            "require_fullscreen": True,
            "allowed_file_extensions": [".pdf", ".png"],
        }
    }
    response = client.put(f"/api/v1/quizzes/{quiz_id}", json=update_payload, headers=teacher_headers)
    assert response.status_code == 200
    
    updated_settings = response.json()["data"]["settings_config"]
    assert updated_settings["timer_duration"] == 120
    assert updated_settings["allow_multiple_attempts"] is True
    assert updated_settings["require_fullscreen"] is True
    assert updated_settings["allowed_file_extensions"] == [".pdf", ".png"]

    # 3. Try to update with invalid settings (timer_duration < 0)
    invalid_payload = {
        "settings_config": {
            "timer_duration": -10,
        }
    }
    response = client.put(f"/api/v1/quizzes/{quiz_id}", json=invalid_payload, headers=teacher_headers)
    # FastAPI/Pydantic validation error
    assert response.status_code == 422
