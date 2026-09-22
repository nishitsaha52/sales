from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = "TCG Partner Portal API"
    APP_ENV: Literal["development", "test", "production"] = "development"
    APP_DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: str = "http://localhost:5173"

    DATABASE_URL: str = (
        "postgresql+asyncpg://partner_portal:partner_portal@localhost:5432/partner_portal"
    )

    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_SECURE: bool = False
    MINIO_BUCKET: str = "partner-portal"

    JWT_SECRET_KEY: str = Field(
        default="change-me-to-a-long-random-secret-before-use", min_length=32
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, ge=1, le=1440)

    SEED_ADMIN_EMAIL: str = "admin@tcgdigital.com"
    SEED_ADMIN_PASSWORD: str = Field(default="ChangeMe123!", min_length=12)
    SEED_ADMIN_NAME: str = "TCG Administrator"

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    def assert_safe_for_production(self) -> None:
        if self.APP_ENV == "production" and self.JWT_SECRET_KEY.startswith("change-me"):
            raise ValueError("JWT_SECRET_KEY must be replaced in production")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.assert_safe_for_production()
    return settings


settings = get_settings()
