from fastapi.testclient import TestClient

from app.main import app


def test_live_endpoint_returns_request_id() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/health/live", headers={"X-Request-ID": "test-request"})

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["X-Request-ID"] == "test-request"


def test_http_errors_use_standard_envelope() -> None:
    with TestClient(app) as client:
        response = client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "HTTP_401"
    assert response.json()["error"]["request_id"]
