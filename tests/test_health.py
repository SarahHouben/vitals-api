"""Test the health endpoint of the FastAPI application."""


def test_health_returns_ok(client):
    """Test the /health endpoint of the API."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
