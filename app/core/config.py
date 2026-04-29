# app/core/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyUrl, field_validator
from typing import Optional
import os


class Settings(BaseSettings):
    """
    Pydantic BaseSettings automatically reads from .env file.
    Type annotations are validated - if DATABASE_URL is missing,
    the app refuses to start.  This is intentional and good.
    """

    # -- Application -------------------------------------------
    APP_NAME: str = "CRM Lead System" # these ones that have values are defaults
    APP_ENV: str = "development"      # that act as a sensible fallback
    DEBUG: bool = False               # so the app runs even if you don't define
                                      # them on your .env file
    # -- Database ----------------------------------------------
    # asyncpg driver -- used by FastAPI for all runtime queries
    DATABASE_URL: str

    # psycopg driver - used ONLY by Alembic (for migrations)
    DATABASE_URL_SYNC: str

    # -- Security ---------------------------------------------
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # -- File Uploads -----------------------------------------
    UPLOAD_DIR: str = "uploads/photos"
    MAX_FILE_SIZE_MB: int = 5

    # -- Computed property (not from .env) --------------------
    @property
    def max_file_size_bytes(self) -> int:
        """Converts MB to bytes for use in upload validation."""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024
    
    # -- Pydantic v2 config -----------------------------------
    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
        case_sensitive = True, # DATABASE_URL <> database_url
        extra = "ignore"       # silently ignore unknown .env keys
    )

# Single instance - imported everywhere else in the app.
# This is the Singleton pattern: one object, shared across the codebase.
settings = Settings()
