"""
Database configuration module.

This module handles database connection and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.base import Base


# Create engine with check_same_thread=False for SQLite
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """
    Initialize the database by creating all tables.

    This function should be called when the application starts.
    """
    Base.metadata.create_all(bind=engine)


# Initialize the database
init_db()
