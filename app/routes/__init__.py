"""Routes blueprint initialization module.

This module defines and exports the main Blueprint for the application.
"""

from flask import Blueprint, Response, jsonify, render_template

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index() -> str:
    """Root endpoint showing the main menu analysis page.

    Returns:
        Rendered HTML template for the main page.
    """
    return render_template("index.html")


@main_bp.route("/health")
def health() -> Response:
    """Health check endpoint.

    Returns:
        JSON response indicating the application is healthy.
    """
    return jsonify(
        {
            "status": "healthy",
        }
    )
