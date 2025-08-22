import pytest


def test_app_imports():
    """Test that the app can be imported without errors"""
    from app.app import app
    assert app is not None


def test_hello_world_endpoint():
    """Test the hello world endpoint without database"""
    from app.app import app
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    response = client.get("/api/hello_world")
    assert response.status_code == 200
    assert response.json() == {"Success": True}


def test_docs_redirect():
    """Test the docs redirect without database"""
    from app.app import app
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
