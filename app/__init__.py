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

    # Default configuration
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret-key"),
        MAX_CONTENT_LENGTH=int(
            os.environ.get("MAX_UPLOAD_SIZE", 10 * 1024 * 1024)
        ),  # 10MB default
        UPLOAD_FOLDER=Path(app.instance_path) / "uploads",
    )

    # Override with custom config if provided
    if config:
        app.config.update(config)

    # Ensure instance and upload folders exist
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)

    # Register blueprints
    from app.routes import main_bp

    app.register_blueprint(main_bp)

    return app
