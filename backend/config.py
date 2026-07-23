from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    database_url: str
    frontend_origins: list[str]
    environment: str = "development"
    demo_user_id: int = 1
    gemini_api_key: str | None = None
    jwt_secret_key: str = "dev-only-change-me-in-production"
    jwt_expiry_minutes: int = 1440  # 24 hours

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
