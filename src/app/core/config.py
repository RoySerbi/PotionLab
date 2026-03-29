from typing import ClassVar

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    database_url: str | None = None  # Env var: POTION_DATABASE_URL; fallback: SQLite
    redis_url: str = "redis://localhost:6379"  # Env var: POTION_REDIS_URL
    app_title: str = "PotionLab"
    app_version: str = "0.1.0"
    jwt_secret: str | None = None
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    google_api_key: str | None = None

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_prefix="POTION_"
    )


settings = Settings()
