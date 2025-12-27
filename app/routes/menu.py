"""Menu analysis route handlers."""

import logging
import time
from io import BytesIO
from typing import Any

from flask import Blueprint, Response, jsonify, request
from PIL import Image
from werkzeug.datastructures import FileStorage

from app.services.ai.base import AIProviderError
from app.services.ai.factory import AIProviderFactory

# ロガーの設定
logger = logging.getLogger(__name__)

menu_bp = Blueprint("menu", __name__, url_prefix="/api")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
ALLOWED_MIME_TYPES = {"image/png", "image/jpeg", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def allowed_file(filename: str) -> bool:
    """
    ファイルの拡張子が許可されているかチェック.

    Args:
        filename: ファイル名

    Returns:
        許可されている場合True
    """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_image_file(file: FileStorage) -> tuple[bool, str | None]:
    """
    画像ファイルをバリデーション.

    Args:
        file: アップロードされたファイル

    Returns:
        (バリデーション結果, エラーメッセージ)
    """
    # ファイル名チェック
    if not file.filename:
        return False, "No filename provided"

    # 拡張子チェック
    if not allowed_file(file.filename):
        return False, f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"

    # MIMEタイプチェック
    if file.content_type not in ALLOWED_MIME_TYPES:
        return False, f"Invalid MIME type: {file.content_type}"

    # ファイルサイズチェック
    file.seek(0, 2)  # ファイルの末尾に移動
    file_size = file.tell()
    file.seek(0)  # ファイルの先頭に戻す

    if file_size > MAX_FILE_SIZE:
        return False, f"File size exceeds limit ({MAX_FILE_SIZE / (1024 * 1024):.0f}MB)"

    if file_size == 0:
        return False, "File is empty"

    # 画像として読み込めるか検証
    try:
        image_data = file.read()
        file.seek(0)  # ファイルの先頭に戻す
        Image.open(BytesIO(image_data))
    except Exception as e:
        logger.error(f"Failed to open image: {e}")
        return False, "Invalid image file"

    return True, None


@menu_bp.route("/analyze", methods=["POST"])
def analyze_menu() -> Response:
    """
    メニュー画像を解析する.

    Request:
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
        JSON形式の解析結果
    """
    start_time = time.time()

    # ファイル存在チェック
    if "image" not in request.files:
        logger.warning("No image file in request")
        return jsonify({"success": False, "error": "No image file provided", "code": "NO_FILE"}), 400

    file = request.files["image"]

    # ファイルが選択されているかチェック
    if file.filename == "":
        logger.warning("Empty filename")
        return jsonify({"success": False, "error": "No file selected", "code": "NO_FILE"}), 400

    # バリデーション
    is_valid, error_message = validate_image_file(file)
    if not is_valid:
        logger.warning(f"Validation failed: {error_message}")
        return jsonify({"success": False, "error": error_message, "code": "INVALID_FILE"}), 400

    try:
        # 画像データを読み込む
        image_data = file.read()
        mime_type = file.content_type or "image/jpeg"

        logger.info(f"Processing image: {file.filename}, size: {len(image_data)} bytes, MIME: {mime_type}")

        # AIプロバイダーを取得
        provider = AIProviderFactory.create()

        # メニュー解析
        result = provider.analyze_menu(image_data, mime_type)

        # レスポンス作成
        response_data: dict[str, Any] = {
            "success": True,
            "dishes": [dish.to_dict() for dish in result.dishes],
            "provider": result.provider,
            "processing_time": time.time() - start_time,
        }

        logger.info(f"Analysis complete: {len(result.dishes)} dishes found in {response_data['processing_time']:.2f}s")

        return jsonify(response_data), 200

    except AIProviderError as e:
        logger.error(f"AI provider error: {e}")
        return (
            jsonify(
                {
                    "success": False,
                    "error": f"AI analysis failed: {str(e)}",
                    "code": "AI_ERROR",
                }
            ),
            500,
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return (
            jsonify(
                {
                    "success": False,
                    "error": "Internal server error",
                    "code": "INTERNAL_ERROR",
                }
            ),
            500,
        )
