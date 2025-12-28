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
from PIL import Image
from werkzeug.datastructures import FileStorage

from app.services.ai.base import AIProviderError, InvalidMenuImageError
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


def _create_error_response(
    error_message: str, error_code: str, status_code: int, title: str = "エラー"
) -> tuple[Response, int]:
    """
    エラーレスポンスを作成（リクエストタイプに応じてJSONまたはHTML）.

    Args:
        error_message: エラーメッセージ
        error_code: エラーコード
        status_code: HTTPステータスコード
        title: HTMLレスポンスのタイトル

    Returns:
        (Response, status_code)のタプル
    """
    # HTMXリクエストの場合はHTMLパーシャルを返す
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

    # 通常のリクエストの場合はJSONを返す
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
    画像ファイルをバリデーション.

    Args:
        file: アップロードされたファイル

    Returns:
        (バリデーション結果, エラーメッセージ, 画像データ)
    """
    # ファイル名チェック
    if not file.filename:
        return False, "No filename provided", None

    # 拡張子チェック
    if not allowed_file(file.filename):
        return False, f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}", None

    # MIMEタイプチェック
    if file.content_type not in ALLOWED_MIME_TYPES:
        return False, f"Invalid MIME type: {file.content_type}", None

    # ファイルを一度だけ読み込む
    file.seek(0)
    image_data = file.read()
    file_size = len(image_data)

    # ファイルサイズチェック
    if file_size > MAX_FILE_SIZE:
        return False, f"File size exceeds limit ({MAX_FILE_SIZE / (1024 * 1024):.0f}MB)", None

    if file_size == 0:
        return False, "File is empty", None

    # 画像として読み込めるか検証
    try:
        Image.open(BytesIO(image_data))
    except (OSError, Image.UnidentifiedImageError) as e:
        logger.error(f"Failed to open image: {e}")
        return False, "Invalid image file", None

    return True, None, image_data


@menu_bp.route("/analyze", methods=["POST"])
def analyze_menu() -> Response:
    """
    メニュー画像を解析する.

    Request:
        Headers:
            X-API-Key: APIキー（必須）
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
    # APIキー取得
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        logger.warning("No API key provided")
        return _create_error_response(
            error_message="APIキーが提供されていません。設定画面からAPIキーを入力してください。",
            error_code="NO_API_KEY",
            status_code=401,
            title="APIキー未設定",
        )

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
    is_valid, error_message, image_data = validate_image_file(file)
    if not is_valid:
        logger.warning(f"Validation failed: {error_message}")
        return jsonify({"success": False, "error": error_message, "code": "INVALID_FILE"}), 400

    try:
        # バリデーション済みの画像データを使用
        # バリデーションで content_type が ALLOWED_MIME_TYPES に含まれることを確認済み
        mime_type = file.content_type

        logger.info(f"Processing image: {file.filename}, size: {len(image_data)} bytes, MIME: {mime_type}")

        # AIプロバイダーを取得
        provider = AIProviderFactory.create(api_key=api_key)

        # メニュー解析
        result = provider.analyze_menu(image_data, mime_type)

        # レスポンス作成
        response_data: dict[str, Any] = {
            "success": True,
            "dishes": [dish.to_dict() for dish in result.dishes],
            "provider": result.provider,
            "processing_time": result.processing_time,
        }

        logger.info(f"Analysis complete: {len(result.dishes)} dishes found in {result.processing_time:.2f}s")

        # HTMXリクエストの場合はHTMLパーシャルを返す
        if request.headers.get("HX-Request") == "true":
            return render_template(
                "partials/dish_list.html",
                dishes=result.dishes,
                provider=result.provider,
                processing_time=response_data["processing_time"],
            )

        return jsonify(response_data), 200

    except InvalidMenuImageError as e:
        logger.warning(f"Invalid menu image: {e}")
        return _create_error_response(
            error_message=str(e),
            error_code="INVALID_MENU_IMAGE",
            status_code=400,
            title="メニュー画像ではありません",
        )
    except AIProviderError as e:
        logger.error(f"AI provider error: {e}")
        return _create_error_response(
            error_message=f"AI解析に失敗しました: {str(e)}",
            error_code="AI_ERROR",
            status_code=500,
            title="AI解析エラー",
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return _create_error_response(
            error_message="予期しないエラーが発生しました。しばらく時間をおいて再度お試しください。",
            error_code="INTERNAL_ERROR",
            status_code=500,
            title="予期しないエラー",
        )
