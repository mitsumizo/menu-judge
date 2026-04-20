"""Menu analysis route handlers.

API Error Codes:
- NO_API_KEY: API key not provided
- NO_FILE: No image file provided or empty filename
- INVALID_FILE: File validation failed (extension, MIME type, size, or format)
- INVALID_MENU_IMAGE: Image does not appear to be a menu
- AI_ERROR: AI provider analysis failed
- INTERNAL_ERROR: Unexpected server error
"""

import logging
from io import BytesIO
from typing import Any

from flask import Blueprint, Response, jsonify, render_template, request
from flask.typing import ResponseReturnValue
from PIL import Image
from werkzeug.datastructures import FileStorage

from app.services.ai.base import AIProviderError, InvalidMenuImageError
from app.services.ai.factory import AIProviderFactory, UnknownProviderError
from app.translations.loader import TranslationLoader

# Logger setup
logger = logging.getLogger(__name__)

menu_bp = Blueprint("menu", __name__, url_prefix="/api")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
ALLOWED_MIME_TYPES = {"image/png", "image/jpeg", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def allowed_file(filename: str) -> bool:
    """
    Check if file extension is allowed.

    Args:
        filename: Filename to check

    Returns:
        True if extension is allowed
    """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def _create_error_response(
    error_message: str, error_code: str, status_code: int, title: str = "Error"
) -> ResponseReturnValue:
    """
    Create error response (JSON or HTML depending on request type).

    Args:
        error_message: Error message
        error_code: Error code
        status_code: HTTP status code
        title: Title for HTML response

    Returns:
        Tuple of (Response, status_code)
    """
    # Return HTML partial for HTMX requests
    if request.headers.get("HX-Request") == "true":
        response = Response(
            render_template(
                "partials/error.html",
                title=title,
                message=error_message,
                code=error_code,
            )
        )
        response.status_code = status_code
        response.headers["X-Error-Code"] = error_code
        return response

    # Return JSON for regular requests
    response = jsonify(
        {
            "success": False,
            "error": error_message,
            "code": error_code,
        }
    )
    response.headers["X-Error-Code"] = error_code
    return response, status_code


def validate_image_file(file: FileStorage) -> tuple[bool, str | None, bytes | None]:
    """
    Validate image file.

    Args:
        file: Uploaded file

    Returns:
        Tuple of (validation result, error message, image data)
    """
    # Check filename
    if not file.filename:
        return False, "No filename provided", None

    # Check extension
    if not allowed_file(file.filename):
        return False, f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}", None

    # Check MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        return False, f"Invalid MIME type: {file.content_type}", None

    # Read file once
    file.seek(0)
    image_data = file.read()
    file_size = len(image_data)

    # Check file size
    if file_size > MAX_FILE_SIZE:
        return False, f"File size exceeds limit ({MAX_FILE_SIZE / (1024 * 1024):.0f}MB)", None

    if file_size == 0:
        return False, "File is empty", None

    # Verify image can be opened
    try:
        Image.open(BytesIO(image_data))
    except (OSError, Image.UnidentifiedImageError) as e:
        logger.exception(f"Failed to open image: {e}")
        return False, "Invalid image file", None

    return True, None, image_data


@menu_bp.route("/analyze", methods=["POST"])
def analyze_menu() -> ResponseReturnValue:
    """
    Analyze menu image.

    Request:
        Headers:
            X-API-Key: API key (required)
            X-Language: Language code ('en' or 'ja', optional, default: 'en')
        Content-Type: multipart/form-data
        Body: image (file)

    Response:
        {
            "success": true,
            "dishes": [...],
            "provider": "claude",
            "processing_time": 1.234
        }

    Returns:
        Analysis results in JSON format
    """
    # Get language from header
    language = request.headers.get("X-Language", "en")
    if language not in ["en", "ja"]:
        language = "en"

    # Get API key
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        logger.warning("No API key provided")
        error_msg = TranslationLoader.get(
            language,
            "toast.api_key_invalid",
            "API key not provided. Please enter your API key in the settings.",
        )
        title_msg = TranslationLoader.get(language, "error.api_key_not_set", "API Key Not Set")
        return _create_error_response(
            error_message=error_msg,
            error_code="NO_API_KEY",
            status_code=401,
            title=title_msg,
        )

    # Check file existence
    if "image" not in request.files:
        logger.warning("No image file in request")
        return jsonify(
            {"success": False, "error": "No image file provided", "code": "NO_FILE"}
        ), 400

    file = request.files["image"]

    # Check if file is selected
    if file.filename == "":
        logger.warning("Empty filename")
        return jsonify({"success": False, "error": "No file selected", "code": "NO_FILE"}), 400

    # Validation
    is_valid, error_message, image_data = validate_image_file(file)
    if not is_valid:
        logger.warning(f"Validation failed: {error_message}")
        return jsonify({"success": False, "error": error_message, "code": "INVALID_FILE"}), 400

    # After successful validation, image_data is bytes and content_type is set.
    assert image_data is not None
    assert file.content_type is not None

    try:
        # Validation confirmed that content_type is in ALLOWED_MIME_TYPES
        mime_type = file.content_type

        # Get AI provider from header (default: claude)
        provider_name = request.headers.get("X-AI-Provider", "claude")

        logger.info(
            f"Processing image: {file.filename}, size: {len(image_data)} bytes, "
            f"MIME: {mime_type}, Language: {language}, Provider: {provider_name}"
        )

        # Get AI provider with language support
        provider = AIProviderFactory.create(
            api_key=api_key, provider_name=provider_name, language=language
        )

        # Analyze menu
        result = provider.analyze_menu(image_data, mime_type)

        # Create response
        response_data: dict[str, Any] = {
            "success": True,
            "dishes": [dish.to_dict() for dish in result.dishes],
            "provider": result.provider,
            "processing_time": result.processing_time,
        }

        logger.info(
            f"Analysis complete: {len(result.dishes)} dishes found in {result.processing_time:.2f}s"
        )

        # Return HTML partial for HTMX requests
        if request.headers.get("HX-Request") == "true":
            return render_template(
                "partials/dish_list.html",
                dishes=result.dishes,
                provider=result.provider,
                processing_time=response_data["processing_time"],
            )

        return jsonify(response_data), 200

    except UnknownProviderError as e:
        logger.warning(f"Unknown provider requested: {e}")
        default_msg = "This provider is not yet implemented."
        error_msg = TranslationLoader.get(
            language, "api_key_modal.provider_not_implemented", default_msg
        )
        title_msg = TranslationLoader.get(
            language, "error.provider_not_implemented", "Provider Not Implemented"
        )
        return _create_error_response(
            error_message=error_msg,
            error_code="PROVIDER_NOT_IMPLEMENTED",
            status_code=400,
            title=title_msg,
        )
    except InvalidMenuImageError as e:
        logger.warning(f"Invalid menu image: {e}")
        error_msg = (
            str(e)
            if str(e)
            else TranslationLoader.get(language, "toast.analysis_failed", "Analysis failed")
        )
        title_msg = TranslationLoader.get(language, "error.invalid_menu_image", "Not a Menu Image")
        return _create_error_response(
            error_message=error_msg,
            error_code="INVALID_MENU_IMAGE",
            status_code=400,
            title=title_msg,
        )
    except AIProviderError as e:
        logger.exception(f"AI provider error: {e}")
        error_msg = TranslationLoader.get(
            language, "toast.analysis_failed", f"AI analysis failed: {str(e)}"
        )
        title_msg = TranslationLoader.get(language, "error.analysis_error", "AI Analysis Error")
        return _create_error_response(
            error_message=error_msg,
            error_code="AI_ERROR",
            status_code=500,
            title=title_msg,
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        error_msg = TranslationLoader.get(
            language, "toast.server_error", "An unexpected error occurred. Please try again later."
        )
        title_msg = TranslationLoader.get(language, "error.unknown_error", "Unexpected Error")
        return _create_error_response(
            error_message=error_msg,
            error_code="INTERNAL_ERROR",
            status_code=500,
            title=title_msg,
        )
