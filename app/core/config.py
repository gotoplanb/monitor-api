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
        OTEL_EXPORTER_OTLP_ENDPOINT: OpenTelemetry collector endpoint
    """

    DATABASE_URL: str
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Monitor API"
    OTEL_EXPORTER_OTLP_ENDPOINT: str | None = None

    model_config = ConfigDict(case_sensitive=True, env_file=".env")


settings = Settings()
