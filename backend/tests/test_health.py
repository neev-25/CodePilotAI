from fastapi.testclient import TestClient

from main import app


def test_health_endpoint_returns_service_status():
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_security_headers_are_present():
    client = TestClient(app)
    response = client.get("/")

    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
