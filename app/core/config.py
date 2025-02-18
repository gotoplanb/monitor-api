"""
Configuration settings module.

This module manages application-wide configuration settings using Pydantic.
"""

import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings.

    Attributes:
        DATABASE_URL: Database connection string
        API_V1_STR: API version prefix
        PROJECT_NAME: Name of the project
    """

    # Get DATABASE_URL from environment or use SQLite as default
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Monitor API"

    @property
    def is_postgres(self) -> bool:
        """Check if database is PostgreSQL."""
        return self.DATABASE_URL.startswith("postgres")

    class Config:
        """Pydantic configuration class."""

        case_sensitive = True


settings = Settings()
