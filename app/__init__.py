"""Flask application factory module.

This module provides the application factory pattern for creating
and configuring the Flask application.
"""

import os
from datetime import datetime
from pathlib import Path

from flask import Flask


def create_app(config: dict | None = None) -> Flask:
    """Create and configure the Flask application.

    Args:
        config: Optional configuration dictionary to override defaults.

    Returns:
        Configured Flask application instance.
    """
    app = Flask(__name__)

    # Validate production environment settings
    # Note: Using ENV instead of FLASK_ENV (deprecated in Flask 2.3.0+)
    secret_key = os.environ.get("SECRET_KEY")
    if os.environ.get("ENV") == "production":
        if not secret_key:
            raise ValueError("SECRET_KEY must be set in production environment")
        if os.environ.get("FLASK_DEBUG") == "1":
            raise ValueError("DEBUG mode must be disabled in production environment")

    # Parse and validate MAX_UPLOAD_SIZE
    max_upload_size_raw = os.environ.get("MAX_UPLOAD_SIZE")
    if max_upload_size_raw is None:
        max_upload_size = 10 * 1024 * 1024  # Default: 10MB
    else:
        try:
            max_upload_size = int(max_upload_size_raw)
        except ValueError:
            raise ValueError(
                f"MAX_UPLOAD_SIZE must be a valid integer, got: '{max_upload_size_raw}'"
            ) from None
        if max_upload_size <= 0:
            raise ValueError(f"MAX_UPLOAD_SIZE must be a positive integer, got: {max_upload_size}")

    # Default configuration
    app.config.update(
        SECRET_KEY=secret_key or "dev-secret-key-change-in-production",
        MAX_CONTENT_LENGTH=max_upload_size,
        UPLOAD_FOLDER=Path(app.instance_path) / "uploads",
    )

    # Override with custom config if provided
    if config:
        app.config.update(config)

    # Validate UPLOAD_FOLDER path to prevent directory traversal
    upload_folder = Path(app.config["UPLOAD_FOLDER"]).resolve()
    instance_path = Path(app.instance_path).resolve()
    if not upload_folder.is_relative_to(instance_path):
        raise ValueError(f"UPLOAD_FOLDER must be within instance directory: {instance_path}")

    # Ensure instance and upload folders exist
    try:
        Path(app.instance_path).mkdir(parents=True, exist_ok=True)
        Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise RuntimeError(
            f"Failed to create required directories at {app.instance_path} "
            f"or {app.config['UPLOAD_FOLDER']}: {e}"
        ) from e

    # Register blueprints
    from app.routes import main_bp

    app.register_blueprint(main_bp)

    # Register context processor for template global functions
    @app.context_processor
    def inject_now():
        """Inject now function into Jinja2 templates."""
        return {"now": datetime.now}

    return app
