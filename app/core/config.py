from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./test.db"
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Monitor API"

    class Config:
        case_sensitive = True

settings = Settings() 