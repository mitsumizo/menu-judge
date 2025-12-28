"""Tests for services and models."""

import os
from unittest.mock import Mock, patch

import pytest

from app.models.dish import Category, Dish, PriceRange
from app.services.ai.base import AnalysisResult, APICallError, APIKeyMissingError
from app.services.ai.claude_provider import ClaudeProvider
from app.services.ai.factory import AIProviderFactory, UnknownProviderError


class TestDishModel:
    """Tests for Dish model."""

    def test_dish_creation(self):
        """Test creating a Dish object with valid data."""
        dish = Dish(
            original_name="Pad Thai",
            japanese_name="パッタイ",
            description="米麺を使ったタイ風焼きそば",
            spiciness=2,
            sweetness=3,
            ingredients=["米麺", "エビ", "卵"],
            allergens=["甲殻類", "卵"],
            category=Category.MAIN,
            price_range=PriceRange.MODERATE,
        )

        assert dish.original_name == "Pad Thai"
        assert dish.japanese_name == "パッタイ"
        assert dish.description == "米麺を使ったタイ風焼きそば"
        assert dish.spiciness == 2
        assert dish.sweetness == 3
        assert dish.ingredients == ["米麺", "エビ", "卵"]
        assert dish.allergens == ["甲殻類", "卵"]
        assert dish.category == Category.MAIN
        assert dish.price_range == PriceRange.MODERATE

    def test_dish_to_dict(self):
        """Test converting Dish to dictionary."""
        dish = Dish(
            original_name="Tom Yum",
            japanese_name="トムヤム",
            description="辛酸っぱいタイ風スープ",
            spiciness=4,
            sweetness=1,
            ingredients=["エビ", "レモングラス"],
            allergens=["甲殻類"],
            category=Category.APPETIZER,
            price_range=PriceRange.EXPENSIVE,
        )

        result = dish.to_dict()

        assert isinstance(result, dict)
        assert result["original_name"] == "Tom Yum"
        assert result["japanese_name"] == "トムヤム"
        assert result["description"] == "辛酸っぱいタイ風スープ"
        assert result["spiciness"] == 4
        assert result["sweetness"] == 1
        assert result["ingredients"] == ["エビ", "レモングラス"]
        assert result["allergens"] == ["甲殻類"]
        assert result["category"] == "appetizer"
        assert result["price_range"] == "$$$"

    def test_dish_validation_spiciness_out_of_range(self):
        """Test validation for spiciness out of range (1-5)."""
        with pytest.raises(ValueError, match="spiciness must be 1-5"):
            Dish(
                original_name="Test",
                japanese_name="テスト",
                description="テスト料理",
                spiciness=6,  # Invalid: out of range
                sweetness=3,
            )

        with pytest.raises(ValueError, match="spiciness must be 1-5"):
            Dish(
                original_name="Test",
                japanese_name="テスト",
                description="テスト料理",
                spiciness=0,  # Invalid: out of range
                sweetness=3,
            )

    def test_dish_validation_sweetness_out_of_range(self):
        """Test validation for sweetness out of range (1-5)."""
        with pytest.raises(ValueError, match="sweetness must be 1-5"):
            Dish(
                original_name="Test",
                japanese_name="テスト",
                description="テスト料理",
                spiciness=3,
                sweetness=6,  # Invalid: out of range
            )

        with pytest.raises(ValueError, match="sweetness must be 1-5"):
            Dish(
                original_name="Test",
                japanese_name="テスト",
                description="テスト料理",
                spiciness=3,
                sweetness=-1,  # Invalid: out of range
            )

    def test_dish_validation_type_error(self):
        """Test validation for incorrect types."""
        with pytest.raises(ValueError, match="spiciness must be an integer"):
            Dish(
                original_name="Test",
                japanese_name="テスト",
                description="テスト料理",
                spiciness="3",  # Invalid: should be int
                sweetness=3,
            )

        with pytest.raises(ValueError, match="sweetness must be an integer"):
            Dish(
                original_name="Test",
                japanese_name="テスト",
                description="テスト料理",
                spiciness=3,
                sweetness=3.5,  # Invalid: should be int
            )

    def test_dish_from_dict_valid(self):
        """Test creating Dish from valid dictionary."""
        data = {
            "original_name": "Curry",
            "japanese_name": "カレー",
            "description": "スパイシーなカレー",
            "spiciness": 3,
            "sweetness": 2,
            "ingredients": ["鶏肉", "野菜", "スパイス"],
            "allergens": ["乳製品"],
            "category": "main",
            "price_range": "$$",
        }

        dish = Dish.from_dict(data)

        assert dish.original_name == "Curry"
        assert dish.japanese_name == "カレー"
        assert dish.description == "スパイシーなカレー"
        assert dish.spiciness == 3
        assert dish.sweetness == 2
        assert dish.ingredients == ["鶏肉", "野菜", "スパイス"]
        assert dish.allergens == ["乳製品"]
        assert dish.category == Category.MAIN
        assert dish.price_range == PriceRange.MODERATE

    def test_dish_from_dict_missing_required_fields(self):
        """Test creating Dish from dictionary with missing required fields."""
        data = {
            "original_name": "Test",
            # Missing: japanese_name, description, spiciness, sweetness
        }

        with pytest.raises(ValueError, match="Missing required fields"):
            Dish.from_dict(data)

    def test_dish_from_dict_with_defaults(self):
        """Test creating Dish from dictionary with optional fields using defaults."""
        data = {
            "original_name": "Simple Dish",
            "japanese_name": "シンプル料理",
            "description": "シンプルな料理",
            "spiciness": 1,
            "sweetness": 1,
            # Optional fields not provided
        }

        dish = Dish.from_dict(data)

        assert dish.ingredients == []
        assert dish.allergens == []
        assert dish.category == Category.OTHER
        assert dish.price_range is None

    def test_dish_from_dict_invalid_category_fallback(self):
        """Test that invalid category falls back to OTHER."""
        data = {
            "original_name": "Test",
            "japanese_name": "テスト",
            "description": "テスト料理",
            "spiciness": 2,
            "sweetness": 2,
            "category": "invalid_category",
        }

        dish = Dish.from_dict(data)
        assert dish.category == Category.OTHER


class TestClaudeProvider:
    """Tests for ClaudeProvider."""

    def test_provider_name(self):
        """Test that provider name is correct."""
        provider = ClaudeProvider()
        assert provider.name == "claude"

    def test_is_available_without_api_key(self, monkeypatch):
        """Test is_available returns False when API key is not set."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        assert ClaudeProvider.is_available() is False

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}, clear=False)
    def test_is_available_with_api_key(self):
        """Test is_available returns True when API key is set."""
        assert ClaudeProvider.is_available() is True

    def test_api_key_missing(self, sample_image, monkeypatch):
        """Test that APIKeyMissingError is raised when API key is not set."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        provider = ClaudeProvider()
        image_data, mime_type = sample_image

        with pytest.raises(APIKeyMissingError, match="ANTHROPIC_API_KEY is not configured"):
            provider.analyze_menu(image_data, mime_type)

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}, clear=False)
    @patch("anthropic.Anthropic")
    def test_analyze_menu_success(self, mock_anthropic_class, sample_image, mock_claude_response):
        """Test successful menu analysis with mocked API."""
        # Setup mock
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client

        # Mock API response
        mock_message = Mock()
        mock_message.content = [Mock(text=mock_claude_response)]
        mock_client.messages.create.return_value = mock_message

        # Test
        provider = ClaudeProvider()
        image_data, mime_type = sample_image
        result = provider.analyze_menu(image_data, mime_type)

        # Verify
        assert isinstance(result, AnalysisResult)
        assert result.provider == "claude"
        assert len(result.dishes) == 2
        assert result.dishes[0].original_name == "Pad Thai"
        assert result.dishes[0].spiciness == 2
        assert result.dishes[1].original_name == "Tom Yum Goong"
        assert result.dishes[1].spiciness == 4
        assert result.processing_time >= 0
        assert mock_claude_response in result.raw_response

        # Verify API was called
        mock_client.messages.create.assert_called_once()

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}, clear=False)
    def test_image_size_exceeds_limit(self, sample_image):
        """Test that APICallError is raised when image size exceeds limit."""
        provider = ClaudeProvider()
        # Create image data larger than MAX_IMAGE_SIZE (10MB)
        large_image_data = b"x" * (ClaudeProvider.MAX_IMAGE_SIZE + 1)
        mime_type = "image/png"

        with pytest.raises(APICallError, match="Image size .* exceeds maximum"):
            provider.analyze_menu(large_image_data, mime_type)

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}, clear=False)
    @patch("anthropic.Anthropic")
    def test_api_error_handling(self, mock_anthropic_class, sample_image):
        """Test API error handling."""
        from anthropic import APIError

        # Setup mock to raise API error
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client

        # Create a proper APIError instance with required arguments
        api_error = APIError(
            message="API Error",
            request=Mock(),
            body=None,
        )
        mock_client.messages.create.side_effect = api_error

        # Test
        provider = ClaudeProvider()
        image_data, mime_type = sample_image

        with pytest.raises(APICallError, match="Claude API call failed"):
            provider.analyze_menu(image_data, mime_type)

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}, clear=False)
    @patch("anthropic.Anthropic")
    def test_parse_response_invalid_json(self, mock_anthropic_class, sample_image):
        """Test error handling for invalid JSON response."""
        # Setup mock with invalid JSON
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client
        mock_message = Mock()
        mock_message.content = [Mock(text="This is not JSON")]
        mock_client.messages.create.return_value = mock_message

        # Test
        provider = ClaudeProvider()
        image_data, mime_type = sample_image

        with pytest.raises(APICallError, match="Failed to parse"):
            provider.analyze_menu(image_data, mime_type)

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}, clear=False)
    @patch("anthropic.Anthropic")
    def test_parse_response_missing_dishes_key(self, mock_anthropic_class, sample_image):
        """Test error handling when response is missing 'dishes' key."""
        # Setup mock with JSON missing 'dishes' key
        mock_client = Mock()
        mock_anthropic_class.return_value = mock_client
        mock_message = Mock()
        mock_message.content = [Mock(text='{"invalid": "structure"}')]
        mock_client.messages.create.return_value = mock_message

        # Test
        provider = ClaudeProvider()
        image_data, mime_type = sample_image

        with pytest.raises(APICallError, match="Failed to parse response"):
            provider.analyze_menu(image_data, mime_type)


class TestAIProviderFactory:
    """Tests for AIProviderFactory."""

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key", "AI_PROVIDER": "claude"}, clear=False)
    def test_create_claude_provider(self):
        """Test creating Claude provider from factory."""
        provider = AIProviderFactory.create()
        assert isinstance(provider, ClaudeProvider)
        assert provider.name == "claude"

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}, clear=False)
    def test_create_with_explicit_provider_name(self):
        """Test creating provider with explicit provider name."""
        provider = AIProviderFactory.create("claude")
        assert isinstance(provider, ClaudeProvider)
        assert provider.name == "claude"

    @patch.dict(os.environ, {}, clear=True)
    def test_unknown_provider_error(self):
        """Test that UnknownProviderError is raised for unknown provider."""
        with pytest.raises(UnknownProviderError, match="Unknown provider: invalid"):
            AIProviderFactory.create("invalid")

    def test_api_key_missing_error(self, monkeypatch):
        """Test that APIKeyMissingError is raised when API key is not configured."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        with pytest.raises(APIKeyMissingError, match="API key not configured"):
            AIProviderFactory.create("claude")

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}, clear=False)
    def test_available_providers(self):
        """Test getting list of available providers."""
        available = AIProviderFactory.available_providers()
        assert isinstance(available, list)
        assert "claude" in available

    def test_available_providers_empty_when_no_keys(self, monkeypatch):
        """Test that available_providers returns empty list when no API keys are configured."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        available = AIProviderFactory.available_providers()
        assert isinstance(available, list)
        assert "claude" not in available
