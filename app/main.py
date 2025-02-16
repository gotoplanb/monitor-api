"""
Main.
"""

from fastapi import FastAPI
from app.core.config import settings
from app.api.endpoints import monitor
from app.database import init_db

# Initialize database
init_db()

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Include routers
app.include_router(monitor.router, prefix=settings.API_V1_STR)
