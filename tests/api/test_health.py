from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient):
    """Test that /health endpoint returns 200 with status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "redis" in data
    assert data["redis"] in ["connected", "unavailable"]
