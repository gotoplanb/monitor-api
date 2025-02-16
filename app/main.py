from fastapi import FastAPI
from app.core.config import settings
from app.api.endpoints import monitor
from app.database import engine
from app.models.base import Base

# Initialize database
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Include routers
app.include_router(monitor.router, prefix=settings.API_V1_STR) 