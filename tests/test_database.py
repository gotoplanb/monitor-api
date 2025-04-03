"""
Tests for database functionality.
"""

import importlib
from unittest.mock import patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app import database
from app.database import init_db


def test_database_initialization():
    """Test that database initialization works."""
    init_db()
    assert True


def test_database_session():
    """Test that database session can be created."""
    test_session = database.SessionLocal()
    assert test_session is not None
    test_session.close()


def test_database_session_context():
    """Test that database session works in a context."""
    test_session = database.SessionLocal()
    assert test_session.is_active
    test_session.close()


@patch("sqlalchemy.create_engine")
def test_database_connection_error(mock_create_engine):
    """Test that database connection errors are handled."""
    mock_create_engine.side_effect = SQLAlchemyError("Connection failed")
    with pytest.raises(SQLAlchemyError):
        # Force module reload to trigger connection error
        importlib.reload(database)


def test_database_table_creation_error():
    """Test that table creation errors are handled."""
    with patch("app.database.Base.metadata.create_all") as mock_create_all:
        mock_create_all.side_effect = SQLAlchemyError("Table creation failed")
        with pytest.raises(SQLAlchemyError):
            init_db()
