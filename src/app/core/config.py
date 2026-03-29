from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    database_url: str | None = None  # Env var: POTION_DATABASE_URL; fallback: SQLite
    app_title: str = "PotionLab"
    app_version: str = "0.1.0"

    model_config = SettingsConfigDict(env_prefix="POTION_")


settings = Settings()
