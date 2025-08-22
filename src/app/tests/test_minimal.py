import pytest
from fastapi.testclient import TestClient


def test_app_can_be_imported():
    """Test that the app can be imported without errors"""
    try:
        from app.app import app
        assert app is not None
        print("✓ App imported successfully")
    except Exception as e:
        pytest.fail(f"Failed to import app: {e}")


def test_hello_world_endpoint():
    """Test the hello world endpoint"""
    try:
        from app.app import app
        client = TestClient(app)
        response = client.get("/api/hello_world")
        assert response.status_code == 200
        assert response.json() == {"Success": True}
        print("✓ Hello world endpoint works")
    except Exception as e:
        pytest.fail(f"Hello world endpoint failed: {e}")


def test_docs_redirect():
    """Test the docs redirect"""
    try:
        from app.app import app
        client = TestClient(app)
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307  # Temporary redirect
        print("✓ Docs redirect works")
    except Exception as e:
        pytest.fail(f"Docs redirect failed: {e}")


def test_app_has_routes():
    """Test that the app has the expected routes"""
    try:
        from app.app import app
        routes = [route.path for route in app.routes]
        print(f"Available routes: {routes}")
        
        # Check for key routes
        assert "/" in routes
        assert "/docs" in routes
        assert "/api/hello_world" in routes
        print("✓ App has expected routes")
    except Exception as e:
        pytest.fail(f"Route check failed: {e}")
