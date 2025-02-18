"""
Tests for monitor endpoints.
"""

import pytest
from datetime import datetime
from app.models.monitor import MonitorState


def test_create_monitor(client):
    """Test creating a new monitor."""
    response = client.post(
        "/api/v1/monitors/",
        json={"name": "test-monitor", "tags": ["test", "production"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test-monitor"
    assert "test" in data["tags"]
    assert "production" in data["tags"]


def test_create_duplicate_monitor(client, sample_monitor):
    """Test creating a monitor with a duplicate name."""
    response = client.post(
        "/api/v1/monitors/", json={"name": "test-monitor", "tags": ["test"]}
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_set_monitor_state(client, sample_monitor):
    """Test setting a monitor's state."""
    response = client.post("/api/v1/monitors/1/state/", json={"state": "Normal"})
    assert response.status_code == 200
    assert response.json()["message"] == "State updated successfully"


def test_set_monitor_state_invalid_monitor(client):
    """Test setting state for non-existent monitor."""
    response = client.post("/api/v1/monitors/999/state/", json={"state": "Normal"})
    assert response.status_code == 404
    assert "Monitor not found" in response.json()["detail"]


def test_get_monitor_state(client, sample_monitor):
    """Test getting a monitor's state."""
    # First set a state
    client.post("/api/v1/monitors/1/state/", json={"state": "Normal"})

    # Then get the state
    response = client.get("/api/v1/monitors/1/state/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test-monitor"
    assert data["state"] == "Normal"
    assert "timestamp" in data
    assert "tags" in data


def test_get_monitor_state_invalid_monitor(client):
    """Test getting state for non-existent monitor."""
    response = client.get("/api/v1/monitors/999/state/")
    assert response.status_code == 404
    assert "Monitor not found" in response.json()["detail"]


def test_get_all_monitor_states_empty(client):
    """Test getting all monitor states when none exist."""
    response = client.get("/api/v1/monitors/statuses/")
    assert response.status_code == 200
    assert response.json() == []


def test_get_all_monitor_states(client, sample_monitor):
    """Test getting all monitor states."""
    # Set states for the monitor
    client.post("/api/v1/monitors/1/state/", json={"state": "Normal"})

    response = client.get("/api/v1/monitors/statuses/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "test-monitor"
    assert data[0]["state"] == "Normal"
    assert "timestamp" in data[0]
    assert "tags" in data[0]


def test_get_monitor_state_badge(client, sample_monitor):
    """Test getting a monitor's state badge."""
    # Set a state first
    client.post("/api/v1/monitors/1/state/", json={"state": "Normal"})

    response = client.get("/api/v1/monitors/1/state/badge.png")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"


def test_get_monitor_state_badge_invalid_monitor(client):
    """Test getting state badge for non-existent monitor."""
    response = client.get("/api/v1/monitors/999/state/badge.png")
    assert response.status_code == 404
    assert "Monitor not found" in response.json()["detail"]


def test_get_monitors_by_tags(client):
    """Test getting monitors filtered by tags."""
    # Create monitors with different tags
    client.post("/api/v1/monitors/", json={"name": "monitor1", "tags": ["prod", "web"]})
    client.post("/api/v1/monitors/", json={"name": "monitor2", "tags": ["prod", "db"]})
    client.post("/api/v1/monitors/", json={"name": "monitor3", "tags": ["dev", "web"]})

    # Set states
    for i in range(1, 4):
        client.post(f"/api/v1/monitors/{i}/state/", json={"state": "Normal"})

    # Test filtering by single tag
    response = client.get("/api/v1/monitors/statuses/by-tags/?tags=prod")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    names = {m["name"] for m in data}
    assert names == {"monitor1", "monitor2"}

    # Test filtering by multiple tags
    response = client.get("/api/v1/monitors/statuses/by-tags/?tags=prod&tags=web")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "monitor1"
