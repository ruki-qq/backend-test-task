import pytest
from loguru import logger


def test_app_can_be_imported():
    """Тест на импорт приложения без ошибок"""

    try:
        from app.app import app

        assert app is not None
        logger.success("App imported successfully")
    except Exception as e:
        pytest.fail(f"Failed to import app: {e}")


def test_app_has_routes():
    """Тест на то, что в приложении присутствуют необходимые рауты"""

    try:
        from app.app import app

        routes = [route.path for route in app.routes]
        logger.debug(f"Available routes: {routes}")

        assert "/" in routes
        assert "/docs" in routes
        assert "/api/channels/" in routes
        assert "/api/channels/{channel_id}" in routes
        assert "/api/channels/{channel_id}/dialogue" in routes
        assert "/api/webhook/new_message" in routes
        print("App has expected routes")
    except Exception as e:
        pytest.fail(f"Route check failed: {e}")
