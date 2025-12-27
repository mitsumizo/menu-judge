"""Routes blueprint initialization module.

This module defines and exports the main Blueprint for the application.
"""

from flask import Blueprint, jsonify

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index() -> dict:
    """Root endpoint returning application status.

    Returns:
        JSON response with application status and message.
    """
    return jsonify({
        "status": "ok",
        "message": "Menu Judge API is running",
    })


@main_bp.route("/health")
def health() -> dict:
    """Health check endpoint.

    Returns:
        JSON response indicating the application is healthy.
    """
    return jsonify({"status": "healthy"})
