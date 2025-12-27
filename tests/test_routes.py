"""Tests for the application routes."""


def test_index_endpoint_returns_status_ok(client):
    """Test that the root endpoint returns status ok."""
    response = client.get("/")

    assert response.status_code == 200
    assert response.json["status"] == "ok"
    assert response.json["message"] == "Menu Judge API is running"


def test_health_endpoint_returns_healthy(client):
    """Test that the health endpoint returns healthy status."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json == {"status": "healthy"}


def test_unknown_endpoint_returns_404(client):
    """Test that unknown endpoints return 404."""
    response = client.get("/unknown-endpoint")

    assert response.status_code == 404
