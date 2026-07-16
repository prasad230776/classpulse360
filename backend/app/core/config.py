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


settings = Settings()
