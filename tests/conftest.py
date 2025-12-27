"""Pytest fixtures for the Menu Judge application."""

import pytest

from app import create_app


@pytest.fixture
def app():
    """Create and configure a test application instance.

    Yields:
        Flask application configured for testing.
    """
    app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
    })
    yield app


@pytest.fixture
def client(app):
    """Create a test client for the application.

    Args:
        app: Flask application fixture.

    Returns:
        Flask test client.
    """
    return app.test_client()
