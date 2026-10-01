"""Test the health endpoint of the FastAPI application."""

from fastapi.testclient import TestClient

from vitals_api.main import app


def test_health_returns_ok():
    """Test the /health endpoint of the API."""
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
