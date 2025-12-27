#!/usr/bin/env python
"""Flask application entry point.

This module serves as the entry point for running the Flask application.
It loads environment variables and starts the development server.
"""

import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app import create_app

app = create_app()

if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    # Default to 0.0.0.0 in debug mode, 127.0.0.1 otherwise for security
    default_host = "0.0.0.0" if debug else "127.0.0.1"
    host = os.environ.get("FLASK_HOST", default_host)
    port = int(os.environ.get("FLASK_PORT", 5000))

    app.run(host=host, port=port, debug=debug)
