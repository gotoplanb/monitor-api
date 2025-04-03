"""
Tests for database configuration and session management.
"""

import pytest
from sqlalchemy.exc import SQLAlchemyError
from app.database import SessionLocal, init_db, engine
from app.models.base import Base
from app.models.monitor import Monitor, MonitorState, monitor_tags


def test_database_initialization():
    """Test that database tables are created during initialization."""
    # Clear any existing tables
    Base.metadata.drop_all(bind=engine)

    # Initialize the database
    init_db()

    # Get all table names
    table_names = set(Base.metadata.tables.keys())

    # Verify all expected tables exist
    assert "monitor" in table_names
    assert "monitor_statuses" in table_names
    assert "monitor_tags" in table_names
    assert "tags" in table_names


def test_database_session():
    """Test that database sessions are properly created and closed."""
    # Get a session
    db = SessionLocal()

    try:
        # Verify session is active
        assert not db.in_transaction()
    finally:
        # Close the session
        db.close()
        assert not db.in_transaction()


def test_database_session_context():
    """Test that database sessions are properly managed in context."""
    # Test session in context manager
    with SessionLocal() as db:
        assert not db.in_transaction()

    # Session should be closed after context
    assert not db.in_transaction()


def test_database_connection_error(monkeypatch):
    """Test handling of database connection errors."""

    # Mock create_engine to raise an error
    def mock_create_engine(*args, **kwargs):
        raise SQLAlchemyError("Connection failed")

    # Import the module here to avoid initialization issues
    import sqlalchemy

    monkeypatch.setattr(sqlalchemy, "create_engine", mock_create_engine)

    # Attempt to initialize database should raise SQLAlchemyError
    with pytest.raises(SQLAlchemyError):
        # We need to reimport the module to trigger the error
        import importlib
        import app.database

        importlib.reload(app.database)


def test_database_table_creation_error(monkeypatch):
    """Test handling of table creation errors."""

    # Mock create_all to raise an error
    def mock_create_all(*args, **kwargs):
        raise SQLAlchemyError("Table creation failed")

    # Patch the create_all method
    monkeypatch.setattr(Base.metadata, "create_all", mock_create_all)

    # Attempt to initialize database should raise SQLAlchemyError
    with pytest.raises(SQLAlchemyError):
        init_db()
