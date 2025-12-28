"""Tests for the application routes."""

from io import BytesIO
from unittest.mock import Mock, patch

import pytest
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
    return img_bytes.read()


@pytest.fixture
def sample_image():
    """テスト用のサンプル画像を提供するフィクスチャ."""
    return create_test_image()


class TestIndexRoute:
    """トップページのルートテスト."""

    def test_index_endpoint_returns_status_ok(self, client):
        """Test that the root endpoint returns status ok."""
        response = client.get("/")

        assert response.status_code == 200
        assert response.json["status"] == "ok"
        assert response.json["message"] == "Menu Judge API is running"

    def test_index_rejects_post_method(self, client):
        """Test that POST method is not allowed on root endpoint."""
        response = client.post("/")

        assert response.status_code == 405


class TestHealthRoute:
    """ヘルスチェックルートのテスト."""

    def test_health_endpoint_returns_healthy(self, client):
        """Test that the health endpoint returns healthy status."""
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json == {"status": "healthy"}

    def test_health_rejects_post_method(self, client):
        """Test that POST method is not allowed on health endpoint."""
        response = client.post("/health")

        assert response.status_code == 405


class TestAnalyzeRoute:
    """メニュー解析エンドポイントのテスト."""

    def test_no_file_error(self, client):
        """ファイル未添付エラーテスト."""
        response = client.post("/api/analyze")
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert data["code"] == "NO_FILE"

    def test_invalid_format_error(self, client):
        """非対応形式エラーテスト."""
        data = {"image": (BytesIO(b"fake"), "test.txt")}
        response = client.post("/api/analyze", data=data)
        assert response.status_code == 400
        assert response.get_json()["code"] == "INVALID_FILE"

    def test_file_too_large_error(self, client):
        """ファイルサイズエラーテスト."""
        large_file = BytesIO(b"x" * (11 * 1024 * 1024))  # 11MB
        data = {"image": (large_file, "test.jpg")}
        response = client.post("/api/analyze", data=data)
        # FlaskのMAX_CONTENT_LENGTHにより413が返される
        assert response.status_code == 413

    @patch("app.routes.menu.AIProviderFactory.create")
    def test_analyze_success(self, mock_factory, client, sample_image):
        """正常系テスト."""
        mock_provider = Mock()
        mock_provider.analyze_menu.return_value = AnalysisResult(
            dishes=[
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
            ],
            raw_response="mock response",
            provider="claude",
            processing_time=1.5,
        )
        mock_factory.return_value = mock_provider

        data = {"image": (BytesIO(sample_image), "menu.jpg")}
        response = client.post("/api/analyze", data=data)

        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True
        assert len(data["dishes"]) == 1

    @patch("app.routes.menu.AIProviderFactory.create")
    def test_analyze_htmx_request(self, mock_factory, client, sample_image):
        """HTMX リクエストテスト."""
        mock_provider = Mock()
        mock_provider.analyze_menu.return_value = AnalysisResult(
            dishes=[
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
            ],
            raw_response="mock response",
            provider="claude",
            processing_time=1.5,
        )
        mock_factory.return_value = mock_provider

        response = client.post(
            "/api/analyze", data={"image": (BytesIO(sample_image), "menu.jpg")}, headers={"HX-Request": "true"}
        )

        assert response.status_code == 200
        assert b"dish-list" in response.data  # パーシャルが返される

    @patch("app.routes.menu.AIProviderFactory.create")
    def test_api_error_handling(self, mock_factory, client, sample_image):
        """APIエラーハンドリングテスト."""
        mock_factory.return_value.analyze_menu.side_effect = AIProviderError("API Error")

        data = {"image": (BytesIO(sample_image), "menu.jpg")}
        response = client.post("/api/analyze", data=data)

        assert response.status_code == 500
        assert response.get_json()["code"] == "AI_ERROR"


def test_unknown_endpoint_returns_404(client):
    """Test that unknown endpoints return 404."""
    response = client.get("/unknown-endpoint")

    assert response.status_code == 404
