"""
Main application module.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
from mangum import Mangum

from app.core.config import settings
from app.api.endpoints import monitor
from app.database import init_db
from app.telemetry import init_telemetry, instrument_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database
try:
    init_db()
    logger.info("Database initialized successfully")
except SQLAlchemyError as e:
    logger.error("Database initialization failed: %s", str(e))
    raise

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Initialize OpenTelemetry
tracer_provider = init_telemetry(service_name=settings.PROJECT_NAME)

# Instrument FastAPI with OpenTelemetry
instrument_app(app, tracer_provider)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(monitor.router, prefix=settings.API_V1_STR)

# Lambda handler
handler = Mangum(app)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
