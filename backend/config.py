"""Application configuration using pydantic-settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from functools import lru_cache
from typing import Union


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "UNJobsHub API"
    app_version: str = "1.4.0"
    debug: bool = False

    # Database - REQUIRED (no default, must be set explicitly)
    # Use PostgreSQL for production (Neon, Supabase, etc.)
    # Example: postgresql://user:pass@host/db
    database_url: str

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT Authentication
    secret_key: str = "default-secret-key-for-crawlers-only"  # Must be overridden in production
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # OpenAI
    openai_api_key: str = ""

    # Email
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""

    # CORS - can be comma-separated string or list
    allowed_origins: Union[str, list[str]] = "http://localhost:3000,http://127.0.0.1:3000"

    # File Upload
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    upload_dir: str = "uploads"

    # Celery
    celery_broker_url: str = ""
    celery_result_backend: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

    @field_validator('allowed_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            # Split by comma and strip whitespace
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set Celery URLs from Redis URL if not specified
        if not self.celery_broker_url:
            self.celery_broker_url = self.redis_url
        if not self.celery_result_backend:
            self.celery_result_backend = self.redis_url


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()



