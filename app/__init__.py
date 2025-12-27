"""Flask application factory module.

This module provides the application factory pattern for creating
and configuring the Flask application.
"""

import os
from pathlib import Path
from typing import Optional

from flask import Flask


def create_app(config: Optional[dict] = None) -> Flask:
    """Create and configure the Flask application.

    Args:
        config: Optional configuration dictionary to override defaults.

    Returns:
        Configured Flask application instance.
    """
    app = Flask(__name__)

    # Validate production environment settings
    secret_key = os.environ.get("SECRET_KEY")
    if os.environ.get("FLASK_ENV") == "production":
        if not secret_key:
            raise ValueError("SECRET_KEY must be set in production environment")
        if os.environ.get("FLASK_DEBUG") == "1":
            raise ValueError("DEBUG mode must be disabled in production environment")

    # Default configuration
    app.config.update(
        SECRET_KEY=secret_key or "dev-secret-key-change-in-production",
        MAX_CONTENT_LENGTH=int(
            os.environ.get("MAX_UPLOAD_SIZE", 10 * 1024 * 1024)
        ),  # 10MB default
        UPLOAD_FOLDER=Path(app.instance_path) / "uploads",
    )

    # Override with custom config if provided
    if config:
        app.config.update(config)

    # Ensure instance and upload folders exist
    try:
        Path(app.instance_path).mkdir(parents=True, exist_ok=True)
        Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise RuntimeError(f"Failed to create required directories: {e}") from e

    # Register blueprints
    from app.routes import main_bp

    app.register_blueprint(main_bp)

    return app
