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
    response = client.post(
        "/api/v1/monitor/", json={"name": "test-monitor", "tags": ["test"]}
    )
    monitor_id = response.json()["id"]

    # Set states for the monitor
    client.post(f"/api/v1/monitor/{monitor_id}/state/", json={"state": "Normal"})

    response = client.get("/api/v1/monitor/statuses/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == monitor_id
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


def test_delete_monitor(client: TestClient):
    """Test deleting a monitor."""
    # Create a monitor first
    response = client.post(
        "/api/v1/monitor/", json={"name": "monitor-to-delete", "tags": ["test"]}
    )
    monitor_id = response.json()["id"]

    # Set a state
    client.post(f"/api/v1/monitor/{monitor_id}/state/", json={"state": "Normal"})

    # Delete the monitor
    response = client.delete(f"/api/v1/monitor/{monitor_id}/")
    assert response.status_code == 200
    assert response.json()["message"] == "Monitor deleted successfully"

    # Verify monitor is deleted
    response = client.get(f"/api/v1/monitor/{monitor_id}/state/")
    assert response.status_code == 404
    assert "Monitor not found" in response.json()["detail"]


def test_delete_nonexistent_monitor(client: TestClient):
    """Test deleting a non-existent monitor."""
    response = client.delete("/api/v1/monitor/999/")
    assert response.status_code == 404
    assert "Monitor not found" in response.json()["detail"]


def test_delete_monitor_cascades_to_statuses(client: TestClient):
    """Test that deleting a monitor also deletes its statuses."""
    # Create a monitor
    response = client.post(
        "/api/v1/monitor/", json={"name": "monitor-with-states", "tags": ["test"]}
    )
    monitor_id = response.json()["id"]

    # Set multiple states
    states = ["Normal", "Warning", "Critical"]
    for state in states:
        client.post(f"/api/v1/monitor/{monitor_id}/state/", json={"state": state})

    # Delete the monitor
    client.delete(f"/api/v1/monitor/{monitor_id}/")

    # Verify the monitor is not in the statuses list
    response = client.get("/api/v1/monitor/statuses/")
    assert response.status_code == 200
    data = response.json()
    assert not any(m["name"] == "monitor-with-states" for m in data)


def test_delete_monitor_preserves_other_monitors(client: TestClient):
    """Test that deleting one monitor doesn't affect other monitors."""
    # Create two monitors
    response1 = client.post(
        "/api/v1/monitor/", json={"name": "monitor1", "tags": ["test"]}
    )
    response2 = client.post(
        "/api/v1/monitor/", json={"name": "monitor2", "tags": ["test"]}
    )
    monitor1_id = response1.json()["id"]
    monitor2_id = response2.json()["id"]

    # Set states for both
    client.post(f"/api/v1/monitor/{monitor1_id}/state/", json={"state": "Normal"})
    client.post(f"/api/v1/monitor/{monitor2_id}/state/", json={"state": "Warning"})

    # Delete first monitor
    client.delete(f"/api/v1/monitor/{monitor1_id}/")

    # Verify second monitor still exists
    response = client.get(f"/api/v1/monitor/{monitor2_id}/state/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "monitor2"
    assert data["state"] == "Warning"


def test_monitor_history_pagination(client: TestClient):
    """Test pagination of monitor history."""
    # Create a monitor
    response = client.post(
        "/api/v1/monitor/", json={"name": "history-monitor", "tags": ["test"]}
    )
    monitor_id = response.json()["id"]

    # Set multiple states
    states = ["Normal", "Warning", "Critical", "Normal", "Warning"]
    for state in states:
        client.post(f"/api/v1/monitor/{monitor_id}/state/", json={"state": state})

    # Test with default pagination (limit=10)
    response = client.get(f"/api/v1/monitor/{monitor_id}/history/")
    assert response.status_code == 200
    data = response.json()
    assert (
        len(data) == 6
    )  # All states should be returned (5 from test + 1 initial state)

    # Test with custom limit
    response = client.get(f"/api/v1/monitor/{monitor_id}/history/?limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["state"] == "Warning"  # Most recent state
    assert data[1]["state"] == "Normal"

    # Test with skip
    response = client.get(f"/api/v1/monitor/{monitor_id}/history/?skip=2&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["state"] == "Critical"
    assert data[1]["state"] == "Warning"


def test_monitor_history_invalid_pagination(client: TestClient):
    """Test invalid pagination parameters."""
    # Create a monitor
    response = client.post(
        "/api/v1/monitor/", json={"name": "pagination-monitor", "tags": ["test"]}
    )
    monitor_id = response.json()["id"]

    # Test negative skip
    response = client.get(f"/api/v1/monitor/{monitor_id}/history/?skip=-1")
    assert response.status_code == 422  # Validation error

    # Test zero limit
    response = client.get(f"/api/v1/monitor/{monitor_id}/history/?limit=0")
    assert response.status_code == 422  # Validation error

    # Test limit too high
    response = client.get(f"/api/v1/monitor/{monitor_id}/history/?limit=101")
    assert response.status_code == 422  # Validation error
