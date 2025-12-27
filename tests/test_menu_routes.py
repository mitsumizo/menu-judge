"""Tests for menu analysis route handlers."""

from io import BytesIO
from unittest.mock import Mock, patch

from PIL import Image

from app.models.dish import Category, Dish, PriceRange
from app.services.ai.base import AIProviderError, AnalysisResult


def create_test_image(format="PNG", size=(100, 100), color="red"):
    """
    テスト用の画像を生成.

    Args:
        format: 画像フォーマット
        size: 画像サイズ
        color: 画像の色

    Returns:
        画像データのバイト列
    """
    img = Image.new("RGB", size, color)
    img_bytes = BytesIO()
    img.save(img_bytes, format=format)
    img_bytes.seek(0)
    return img_bytes


def create_mock_result():
    """
    モックの解析結果を生成.

    Returns:
        AnalysisResult: モックの解析結果
    """
    dishes = [
        Dish(
            original_name="Pad Thai",
            japanese_name="パッタイ",
            description="米麺を使ったタイ風焼きそば",
            spiciness=2,
            sweetness=3,
            ingredients=["米麺", "エビ", "卵", "もやし", "ピーナッツ"],
            allergens=["甲殻類", "卵", "ナッツ"],
            category=Category.MAIN,
            price_range=PriceRange.MODERATE,
        )
    ]
    return AnalysisResult(dishes=dishes, raw_response="mock response", provider="mock", processing_time=1.0)


class TestAnalyzeMenuEndpoint:
    """メニュー解析エンドポイントのテスト."""

    def test_no_file_provided(self, client):
        """ファイルが送信されない場合、エラーを返す."""
        response = client.post("/api/analyze")

        assert response.status_code == 400
        assert response.json["success"] is False
        assert response.json["code"] == "NO_FILE"
        assert "No image file provided" in response.json["error"]

    def test_empty_filename(self, client):
        """ファイル名が空の場合、エラーを返す."""
        response = client.post("/api/analyze", data={"image": (BytesIO(b""), "")})

        assert response.status_code == 400
        assert response.json["success"] is False
        assert response.json["code"] == "NO_FILE"
        assert "No file selected" in response.json["error"]

    def test_invalid_file_extension(self, client):
        """無効な拡張子の場合、エラーを返す."""
        response = client.post("/api/analyze", data={"image": (BytesIO(b"test"), "test.txt")})

        assert response.status_code == 400
        assert response.json["success"] is False
        assert response.json["code"] == "INVALID_FILE"
        assert "File type not allowed" in response.json["error"]

    def test_invalid_mime_type(self, client):
        """無効なMIMEタイプの場合、エラーを返す."""
        response = client.post(
            "/api/analyze",
            data={"image": (BytesIO(b"test"), "test.png")},
            content_type="multipart/form-data",
        )
        # Werkzeugは自動的にMIMEタイプを推測するので、明示的に設定する必要がある
        # ここでは、画像ではないデータを送信してテストする
        img_bytes = BytesIO(b"not an image")
        response = client.post(
            "/api/analyze",
            data={"image": (img_bytes, "test.gif")},
        )

        assert response.status_code == 400
        assert response.json["success"] is False
        assert response.json["code"] == "INVALID_FILE"

    def test_file_too_large(self, client):
        """ファイルサイズが大きすぎる場合、エラーを返す."""
        # 11MBのデータを生成
        large_data = b"0" * (11 * 1024 * 1024)
        img_bytes = BytesIO(large_data)

        response = client.post("/api/analyze", data={"image": (img_bytes, "test.png")})

        # FlaskのMAX_CONTENT_LENGTHにより413が返される
        assert response.status_code == 413

    def test_empty_file(self, client):
        """空のファイルの場合、エラーを返す."""
        img_bytes = BytesIO(b"")

        response = client.post("/api/analyze", data={"image": (img_bytes, "test.png")})

        assert response.status_code == 400
        assert response.json["success"] is False
        assert response.json["code"] == "INVALID_FILE"
        assert "File is empty" in response.json["error"]

    def test_invalid_image_data(self, client):
        """無効な画像データの場合、エラーを返す."""
        img_bytes = BytesIO(b"not a valid image")

        response = client.post("/api/analyze", data={"image": (img_bytes, "test.png")})

        assert response.status_code == 400
        assert response.json["success"] is False
        assert response.json["code"] == "INVALID_FILE"
        assert "Invalid image file" in response.json["error"]

    @patch("app.routes.menu.AIProviderFactory.create")
    def test_successful_analysis_png(self, mock_factory, client):
        """PNG画像の解析が成功する."""
        # モックの設定
        mock_provider = Mock()
        mock_provider.analyze_menu.return_value = create_mock_result()
        mock_factory.return_value = mock_provider

        # テスト画像を生成
        img_bytes = create_test_image(format="PNG")

        response = client.post(
            "/api/analyze",
            data={"image": (img_bytes, "test.png")},
            content_type="multipart/form-data",
        )

        assert response.status_code == 200
        assert response.json["success"] is True
        assert len(response.json["dishes"]) == 1
        assert response.json["dishes"][0]["original_name"] == "Pad Thai"
        assert response.json["provider"] == "mock"
        assert "processing_time" in response.json
        assert mock_provider.analyze_menu.called

    @patch("app.routes.menu.AIProviderFactory.create")
    def test_successful_analysis_jpeg(self, mock_factory, client):
        """JPEG画像の解析が成功する."""
        # モックの設定
        mock_provider = Mock()
        mock_provider.analyze_menu.return_value = create_mock_result()
        mock_factory.return_value = mock_provider

        # テスト画像を生成
        img_bytes = create_test_image(format="JPEG")

        response = client.post(
            "/api/analyze",
            data={"image": (img_bytes, "test.jpg")},
            content_type="multipart/form-data",
        )

        assert response.status_code == 200
        assert response.json["success"] is True
        assert len(response.json["dishes"]) == 1

    @patch("app.routes.menu.AIProviderFactory.create")
    def test_successful_analysis_webp(self, mock_factory, client):
        """WebP画像の解析が成功する."""
        # モックの設定
        mock_provider = Mock()
        mock_provider.analyze_menu.return_value = create_mock_result()
        mock_factory.return_value = mock_provider

        # テスト画像を生成
        img_bytes = create_test_image(format="WEBP")

        response = client.post(
            "/api/analyze",
            data={"image": (img_bytes, "test.webp")},
            content_type="multipart/form-data",
        )

        assert response.status_code == 200
        assert response.json["success"] is True
        assert len(response.json["dishes"]) == 1

    @patch("app.routes.menu.AIProviderFactory.create")
    def test_ai_provider_error(self, mock_factory, client):
        """AIプロバイダーエラーの場合、エラーを返す."""
        # モックの設定
        mock_provider = Mock()
        mock_provider.analyze_menu.side_effect = AIProviderError("API error")
        mock_factory.return_value = mock_provider

        # テスト画像を生成
        img_bytes = create_test_image(format="PNG")

        response = client.post(
            "/api/analyze",
            data={"image": (img_bytes, "test.png")},
            content_type="multipart/form-data",
        )

        assert response.status_code == 500
        assert response.json["success"] is False
        assert response.json["code"] == "AI_ERROR"
        assert "AI analysis failed" in response.json["error"]

    @patch("app.routes.menu.AIProviderFactory.create")
    def test_unexpected_error(self, mock_factory, client):
        """予期しないエラーの場合、エラーを返す."""
        # モックの設定
        mock_provider = Mock()
        mock_provider.analyze_menu.side_effect = Exception("Unexpected error")
        mock_factory.return_value = mock_provider

        # テスト画像を生成
        img_bytes = create_test_image(format="PNG")

        response = client.post(
            "/api/analyze",
            data={"image": (img_bytes, "test.png")},
            content_type="multipart/form-data",
        )

        assert response.status_code == 500
        assert response.json["success"] is False
        assert response.json["code"] == "INTERNAL_ERROR"
        assert "Internal server error" in response.json["error"]
