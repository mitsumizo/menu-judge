"""Pytest fixtures for the Menu Judge application."""

import base64
from io import BytesIO

import pytest
from PIL import Image

from app import create_app
from app.models.dish import Category, Dish
from app.services.ai.base import AnalysisResult


@pytest.fixture
def app():
    """Create and configure a test application instance.

    Yields:
        Flask application configured for testing.
    """
    app = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret-key",
        }
    )
    yield app


@pytest.fixture
def client(app):
    """Create a test client for the application.

    Args:
        app: Flask application fixture.

    Returns:
        Flask test client.
    """
    return app.test_client()


@pytest.fixture
def sample_image():
    """Create a sample test image.

    Returns:
        Tuple of (image_data: bytes, mime_type: str)
    """
    # 1x1 pixel PNG image (base64 encoded)
    png_base64 = (
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    )
    image_data = base64.b64decode(png_base64)
    return (image_data, "image/png")


@pytest.fixture
def mock_claude_response():
    """Create a mock Claude API response.

    Returns:
        Mock response data as JSON string
    """
    return """```json
{
  "dishes": [
    {
      "original_name": "Pad Thai",
      "japanese_name": "パッタイ",
      "description": "米麺を使ったタイ風焼きそば。エビ、卵、もやし、ピーナッツを使用",
      "spiciness": 2,
      "sweetness": 3,
      "ingredients": ["米麺", "エビ", "卵", "もやし", "ピーナッツ"],
      "allergens": ["甲殻類", "卵", "ナッツ"],
      "category": "main",
      "price_range": "$$"
    },
    {
      "original_name": "Tom Yum Goong",
      "japanese_name": "トムヤムクン",
      "description": "辛酸っぱいタイ風エビスープ",
      "spiciness": 4,
      "sweetness": 1,
      "ingredients": ["エビ", "レモングラス", "ライム", "唐辛子"],
      "allergens": ["甲殻類"],
      "category": "appetizer",
      "price_range": "$$$"
    }
  ]
}
```"""


@pytest.fixture
def real_menu_image():
    """テスト用のメニュー画像を生成（統合テスト用）.

    Returns:
        bytes: JPEG形式の画像データ
    """
    img = Image.new("RGB", (800, 600), color="white")
    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    buffer.seek(0)
    return buffer.read()


@pytest.fixture
def mock_analysis_result():
    """モックの解析結果を生成.

    Returns:
        AnalysisResult: モックの解析結果
    """
    dishes = [
        Dish(
            original_name="Pad Thai",
            japanese_name="パッタイ",
            description="タイ風焼きそば",
            spiciness=2,
            sweetness=3,
            ingredients=["米麺", "エビ", "卵"],
            allergens=["甲殻類", "卵"],
            category=Category.MAIN,
        )
    ]
    return AnalysisResult(
        dishes=dishes, raw_response="...", provider="claude", processing_time=1.5
    )
