"""
Database configuration module.

This module handles database connection and session management.
"""

import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.models.base import Base

logger = logging.getLogger(__name__)

try:
    # Configure PostgreSQL engine
    db_url = settings.DATABASE_URL
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)

    logger.info("Connecting to PostgreSQL database")
    engine = create_engine(db_url, pool_size=5, max_overflow=10)

    # Create SessionLocal class
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    logger.info("Database connection established successfully")

except SQLAlchemyError as e:
    logger.error("Database connection failed: %s", str(e))
    raise


def init_db() -> None:
    """
    Initialize the database by creating all tables.

    This function should be called when the application starts.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except SQLAlchemyError as e:
        logger.error("Failed to create database tables: %s", str(e))
        raise


# Initialize the database
init_db()
