#!/usr/bin/env python
"""Flask application entry point.

This module serves as the entry point for running the Flask application.
It loads environment variables and starts the development server.
"""

import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from app import create_app  # noqa: E402 (must load .env first)

app = create_app()

if __name__ == "__main__":
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"

    # WARNING: 0.0.0.0 exposes the server to your local network
    # For production, use a proper WSGI server (Gunicorn, uWSGI)
    default_host = "0.0.0.0" if debug else "127.0.0.1"
    host = os.environ.get("FLASK_HOST", default_host)
    port = int(os.environ.get("FLASK_PORT", 5000))

    if not debug:
        print("WARNING: Flask development server is not suitable for production.")
        print("Consider using Gunicorn: gunicorn -w 4 'app:create_app()'")

    app.run(host=host, port=port, debug=debug)
