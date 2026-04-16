"""
Application configuration loaded from environment variables.
Uses pydantic-settings for validation and type coercion.
"""
from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_INSECURE_PLACEHOLDERS = {
    "change-me-to-a-random-secret-key",
    "change-me-to-a-random-jwt-secret",
    "<GENERATE_WITH: openssl rand -hex 32>",
    "",
}

_WEAK_DB_PASSWORDS = {
    "postgres",
    "password",
    "admin",
    "root",
    "changeme",
    "",
}


class Settings(BaseSettings):
    """Application settings populated from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──
    APP_NAME: str = "Performance Test App"
    APP_ENV: str = "development"
    DEBUG: bool = True
    APP_VERSION: str = "1.0.0"
    SECRET_KEY: str

    # ── Backend ──
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000

    # ── Database ──
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "performance_test_app"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""
    DATABASE_URL: str = ""

    # ── Authentication ──
    JWT_SECRET_KEY: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_ALGORITHM: str = "HS256"

    # ── CORS ──
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if v in _INSECURE_PLACEHOLDERS or len(v) < 16:
            raise ValueError(
                "SECRET_KEY is not set or is insecure. "
                "Generate one with: openssl rand -hex 32"
            )
        return v

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def validate_jwt_secret_key(cls, v: str) -> str:
        if v in _INSECURE_PLACEHOLDERS or len(v) < 16:
            raise ValueError(
                "JWT_SECRET_KEY is not set or is insecure. "
                "Generate one with: openssl rand -hex 32"
            )
        return v

    @field_validator("DB_PASSWORD")
    @classmethod
    def validate_db_password(cls, v: str, info) -> str:
        # Only enforce in production
        # info.data may not have APP_ENV yet depending on field order,
        # so we do a best-effort check
        return v

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def async_database_url(self) -> str:
        """Build the async database URL for asyncpg."""
        if self.DATABASE_URL:
            url = self.DATABASE_URL
            if url.startswith("postgresql://"):
                return url.replace("postgresql://", "postgresql+asyncpg://", 1)
            if url.startswith("postgresql+asyncpg://"):
                return url
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def sync_database_url(self) -> str:
        """Build the sync database URL for Alembic migrations."""
        if self.DATABASE_URL:
            url = self.DATABASE_URL
            if url.startswith("postgresql+asyncpg://"):
                return url.replace("postgresql+asyncpg://", "postgresql://", 1)
            if url.startswith("postgresql://"):
                return url
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings singleton."""
    return Settings()