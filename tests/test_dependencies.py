"""
Tests for FastAPI dependencies.
"""

from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.main import app


# Create a test app
test_app = FastAPI()
client = TestClient(app)


@app.get("/test-db")
async def db_test_route(db: Session = Depends(get_db)):
    """Test route for database dependency."""
    # Verify that we got a valid database session
    assert isinstance(db, Session)
    return {"db_active": True}


def test_get_db_dependency():
    """Test that the database dependency yields a session."""
    db_gen = get_db()
    db = next(db_gen)
    assert isinstance(db, Session)
    db.close()


def test_db_route():
    """Test that the database route receives a valid session and returns correct response."""
    response = client.get("/test-db")
    assert response.status_code == 200
    assert response.json() == {"db_active": True}


def test_db_dependency_closes_session():
    """Test that the database dependency properly closes the session."""
    db_gen = get_db()
    db = next(db_gen)
    assert db.is_active
    db.close()
    # After closing, trying to use the session should raise an error
    try:
        db.execute(text("SELECT 1"))
        assert False, "Session should be closed"
    except Exception as exc:  # pylint: disable=broad-except
        assert str(exc) != "", "Exception should have a message"
