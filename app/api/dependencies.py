"""
Database dependency module.

This module provides dependencies for database session management in FastAPI routes.
"""

from typing import Generator
from app.database import SessionLocal


def get_db() -> Generator:
    """
    Create and yield a database session.

    Yields:
        Generator: SQLAlchemy database session

    Example:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
