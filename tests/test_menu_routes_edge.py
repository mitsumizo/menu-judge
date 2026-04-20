"""Edge-case coverage for app.routes.menu — uncovered branches."""

from io import BytesIO
from unittest.mock import MagicMock

from app.routes.menu import MAX_FILE_SIZE, validate_image_file


class TestValidateImageFile:
    def test_empty_filename_returns_error(self):
        file = MagicMock()
        file.filename = ""
        ok, error, data = validate_image_file(file)
        assert ok is False
        assert error == "No filename provided"
        assert data is None

    def test_none_filename_returns_error(self):
        file = MagicMock()
        file.filename = None
        ok, error, data = validate_image_file(file)
        assert ok is False
        assert error == "No filename provided"

    def test_file_exceeds_max_size(self):
        oversized = b"\x00" * (MAX_FILE_SIZE + 1)
        file = MagicMock()
        file.filename = "big.png"
        file.content_type = "image/png"
        file.read.return_value = oversized
        ok, error, data = validate_image_file(file)
        assert ok is False
        assert "exceeds limit" in error
        assert data is None


class TestAnalyzeMenuNoApiKey:
    """Use raw test_client (no auto X-API-Key injection) to hit the NO_API_KEY branch."""

    def test_missing_api_key_returns_401(self, app):
        raw_client = app.test_client()
        response = raw_client.post("/api/analyze")
        assert response.status_code == 401
        assert response.json["success"] is False
        assert response.json["code"] == "NO_API_KEY"

    def test_missing_api_key_htmx_returns_html(self, app):
        raw_client = app.test_client()
        response = raw_client.post("/api/analyze", headers={"HX-Request": "true"})
        assert response.status_code == 401
        assert response.content_type.startswith("text/html")
        assert response.headers.get("X-Error-Code") == "NO_API_KEY"


class TestAnalyzeMenuInvalidLanguage:
    def test_invalid_language_falls_back_to_english(self, client):
        response = client.post("/api/analyze", headers={"X-Language": "fr"})
        # Reaches NO_FILE path — language fallback happened silently before
        assert response.status_code == 400
        assert response.json["code"] == "NO_FILE"
