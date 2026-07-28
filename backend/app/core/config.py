import os
from pydantic_settings import BaseSettings
from functools import lru_cache

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class Settings(BaseSettings):
    """Unified application configuration loaded from environment variables."""

    # Database
    DATABASE_URL: str = "sqlite:///./database/skillsense_dev.db"

    # Security — set these via environment variables or .env
    AES_SECRET_KEY_B64: str = ""
    JWT_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # External APIs
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""

    # AWS Cloud Provisioning
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_DEFAULT_REGION: str = "us-east-1"

    # Application
    APP_NAME: str = "SkillSense AI Unified Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    model_config = {
        "env_file": os.path.join(_BASE_DIR, ".env"),
        "case_sensitive": True,
    }


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton to avoid repeated env parsing."""
    return Settings()
