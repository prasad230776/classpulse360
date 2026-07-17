from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    PROJECT_NAME: str = "ClassPulse360"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: Literal["development", "staging", "production", "testing"] = "development"

    # Database Settings fallback
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/postgres"

    # JWT Settings
    SECRET_KEY: str = "3aefbe87f98d02341258d4fe83bc0f1cfb36ad8efc404f2d348e3cf3e9c40212"  # Fallback for dev only
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7


settings = Settings()
