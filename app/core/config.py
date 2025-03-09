"""
Configuration settings module.

This module manages application-wide configuration settings using Pydantic.
"""

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings.

    Attributes:
        DATABASE_URL: Database connection string
        API_V1_STR: API version prefix
        PROJECT_NAME: Name of the project
    """

    DATABASE_URL: str
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Monitor API"

    model_config = ConfigDict(case_sensitive=True, env_file=".env")


settings = Settings()
