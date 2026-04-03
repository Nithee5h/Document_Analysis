import base64
from fastapi.testclient import TestClient
from src.main import app
from src.core.config import settings


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200


def test_auth_failure() -> None:
    payload = {
        "fileName": "sample.pdf",
        "fileType": "pdf",
        "fileBase64": base64.b64encode(b"dummy").decode(),
    }
    response = client.post("/api/document-analyze", json=payload)
    assert response.status_code == 401


def test_invalid_payload() -> None:
    response = client.post(
        "/api/document-analyze",
        headers={"x-api-key": settings.api_key},
        json={"fileName": "a", "fileType": "txt", "fileBase64": "abc"},
    )
    assert response.status_code in {400, 422}