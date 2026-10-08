from pathlib import Path
from typing import Literal

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.config.celery_config import REDIS_URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    UPLOAD_DIR: Path = Field(default=Path("./uploads"))
    FILE_AGE_THRESHOLD: int = Field(default=86400, description="Age in seconds (24h)")

    # Google OAuth
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_SECRET_KEY: str | None = None
    GOOGLE_SESSION_SECRET: str | None = None

    # JWT
    JWT_SECRET_KEY: str = Field(default="change-me-in-production")
    JWT_ALGORITHM: str = Field(default="HS256")

    # Database Settings
    DB_USER: str = Field(default="postgres")
    DB_PASS: str | None = None
    DB_HOST: str = Field(default="localhost")
    DB_PORT: int = Field(default=5432)
    DB_NAME: str = Field(default="postgres")

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    ADMIN_CRON_SECRET: str | None = None

    ENVIRONMENT: Literal["development", "production"] = Field(
        default="development", description="Environment type"
    )

    REDIS_URL: str = Field(default=REDIS_URL, description="Redis connection URL")

    @computed_field
    @property
    def TORTOISE_DATABASE_URL(self) -> str:
        """Constructs a Tortoise-compatible postgres connection string."""
        auth = f"{self.DB_USER}:{self.DB_PASS}@" if self.DB_PASS else f"{self.DB_USER}@"
        return f"postgres://{auth}{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()
