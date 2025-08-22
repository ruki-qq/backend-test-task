from fastapi import status
from fastapi.testclient import TestClient

from app.app import app


def test_hello_world() -> None:
    client = TestClient(app)
    response = client.get("/api/hello_world")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"Success": True}
