"""
Tests for monitor endpoints.
"""

from fastapi.testclient import TestClient


def test_create_monitor(client: TestClient):
    """Test creating a new monitor."""
    response = client.post(
        "/api/v1/monitor/",
        json={"name": "test-monitor", "tags": ["test", "production"]},
    )
    assert response.status_code == 200, f"Failed with response: {response.text}"
    data = response.json()
    assert data["name"] == "test-monitor"
    assert "test" in data["tags"]
    assert "production" in data["tags"]


def test_create_duplicate_monitor(client: TestClient):
    """Test creating a monitor with a duplicate name."""
    # First create a monitor
    client.post("/api/v1/monitor/", json={"name": "test-monitor", "tags": ["test"]})

    # Try to create duplicate
    response = client.post(
        "/api/v1/monitor/", json={"name": "test-monitor", "tags": ["test"]}
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_set_monitor_state(client: TestClient):
    """Test setting a monitor's state."""
    # First create a monitor
    client.post("/api/v1/monitor/", json={"name": "test-monitor", "tags": ["test"]})

    response = client.post("/api/v1/monitor/1/state/", json={"state": "Normal"})
    assert response.status_code == 200
    assert response.json()["message"] == "State updated successfully"


def test_set_monitor_state_invalid_monitor(client: TestClient):
    """Test setting state for non-existent monitor."""
    response = client.post("/api/v1/monitor/999/state/", json={"state": "Normal"})
    assert response.status_code == 404
    assert "Monitor not found" in response.json()["detail"]


def test_get_monitor_state(client: TestClient):
    """Test getting a monitor's state."""
    # First create a monitor
    client.post("/api/v1/monitor/", json={"name": "test-monitor", "tags": ["test"]})

    # Set a state
    client.post("/api/v1/monitor/1/state/", json={"state": "Normal"})

    # Then get the state
    response = client.get("/api/v1/monitor/1/state/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test-monitor"
    assert data["state"] == "Normal"
    assert "timestamp" in data
    assert "tags" in data


def test_get_monitor_state_invalid_monitor(client: TestClient):
    """Test getting state for non-existent monitor."""
    response = client.get("/api/v1/monitor/999/state/")
    assert response.status_code == 404
    assert "Monitor not found" in response.json()["detail"]


def test_get_all_monitor_states_empty(client: TestClient):
    """Test getting all monitor states when none exist."""
    response = client.get("/api/v1/monitor/statuses/")
    assert response.status_code == 200
    assert response.json() == []


def test_get_all_monitor_states(client: TestClient):
    """Test getting all monitor states."""
    # Create a monitor
    client.post("/api/v1/monitor/", json={"name": "test-monitor", "tags": ["test"]})

    # Set states for the monitor
    client.post("/api/v1/monitor/1/state/", json={"state": "Normal"})

    response = client.get("/api/v1/monitor/statuses/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "test-monitor"
    assert data[0]["state"] == "Normal"
    assert "timestamp" in data[0]
    assert "tags" in data[0]


def test_get_monitor_state_badge(client: TestClient):
    """Test getting a monitor's state badge."""
    # Create a monitor
    client.post("/api/v1/monitor/", json={"name": "test-monitor", "tags": ["test"]})

    # Set a state first
    client.post("/api/v1/monitor/1/state/", json={"state": "Normal"})

    response = client.get("/api/v1/monitor/1/state/badge.png")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"


def test_get_monitor_state_badge_invalid_monitor(client: TestClient):
    """Test getting state badge for non-existent monitor."""
    response = client.get("/api/v1/monitor/999/state/badge.png")
    assert response.status_code == 404
    assert "Monitor not found" in response.json()["detail"]


def test_get_monitors_by_tags(client: TestClient):
    """Test getting monitors filtered by tags."""
    # Create monitors with different tags
    client.post("/api/v1/monitor/", json={"name": "monitor1", "tags": ["prod", "web"]})
    client.post("/api/v1/monitor/", json={"name": "monitor2", "tags": ["prod", "db"]})
    client.post("/api/v1/monitor/", json={"name": "monitor3", "tags": ["dev", "web"]})

    # Set states
    for i in range(1, 4):
        client.post(f"/api/v1/monitor/{i}/state/", json={"state": "Normal"})

    # Test filtering by single tag
    response = client.get("/api/v1/monitor/statuses/by-tags/?tags=prod")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    monitor_names = {m["name"] for m in data}
    assert monitor_names == {"monitor1", "monitor2"}
    for monitor in data:
        assert "prod" in monitor["tags"]

    # Test filtering by multiple tags
    response = client.get("/api/v1/monitor/statuses/by-tags/?tags=prod&tags=web")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "monitor1"
    assert all(tag in data[0]["tags"] for tag in ["prod", "web"])
