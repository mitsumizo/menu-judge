"""Tests for the application factory."""

import os

import pytest

from app import create_app


def test_create_app_returns_flask_instance():
    """Test that create_app returns a Flask application instance."""
    app = create_app()

    assert app is not None
    assert app.name == "app"


def test_create_app_with_custom_config():
    """Test that create_app accepts custom configuration."""
    custom_config = {
        "TESTING": True,
        "SECRET_KEY": "custom-test-key",
    }
    app = create_app(custom_config)

    assert app.config["TESTING"] is True
    assert app.config["SECRET_KEY"] == "custom-test-key"


def test_create_app_requires_secret_key_in_production(monkeypatch):
    """Test that SECRET_KEY is required in production environment."""
    monkeypatch.setenv("FLASK_ENV", "production")
    monkeypatch.delenv("SECRET_KEY", raising=False)

    with pytest.raises(ValueError) as exc_info:
        create_app()

    assert "SECRET_KEY must be set in production" in str(exc_info.value)


def test_create_app_uses_secret_key_from_env(monkeypatch):
    """Test that SECRET_KEY is loaded from environment variable."""
    monkeypatch.setenv("SECRET_KEY", "env-secret-key")
    app = create_app()

    assert app.config["SECRET_KEY"] == "env-secret-key"
