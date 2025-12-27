"""Tests for AI provider base classes."""

import json
import os
from unittest.mock import MagicMock, patch

import pytest

from app.models.dish import Category, Dish, PriceRange
from app.services.ai.base import (
    AIProvider,
    AIProviderError,
    AnalysisResult,
    APICallError,
    APIKeyMissingError,
)
from app.services.ai.claude_provider import ClaudeProvider


class TestAnalysisResult:
    """Test cases for AnalysisResult dataclass."""

    def test_analysis_result_creation(self):
        """Test creating an AnalysisResult with all fields."""
        dish1 = Dish(
            original_name="Pad Thai",
            japanese_name="パッタイ",
            description="米麺を使ったタイ風焼きそば",
            spiciness=2,
            sweetness=3,
            ingredients=["米麺", "エビ"],
            allergens=["甲殻類"],
            category=Category.MAIN,
            price_range=PriceRange.MODERATE,
        )

        dish2 = Dish(
            original_name="Tom Yum Soup",
            japanese_name="トムヤムスープ",
            description="辛酸っぱいタイ風スープ",
            spiciness=4,
            sweetness=1,
            ingredients=["エビ", "レモングラス", "唐辛子"],
            allergens=["甲殻類"],
            category=Category.APPETIZER,
            price_range=PriceRange.BUDGET,
        )

        result = AnalysisResult(
            dishes=[dish1, dish2],
            raw_response='{"dishes": [...]}',
            provider="claude",
            processing_time=1.23,
        )

        assert len(result.dishes) == 2
        assert result.dishes[0].original_name == "Pad Thai"
        assert result.dishes[1].original_name == "Tom Yum Soup"
        assert result.raw_response == '{"dishes": [...]}'
        assert result.provider == "claude"
        assert result.processing_time == 1.23

    def test_analysis_result_with_empty_dishes(self):
        """Test AnalysisResult with empty dishes list."""
        result = AnalysisResult(
            dishes=[],
            raw_response="No dishes found",
            provider="openai",
            processing_time=0.5,
        )

        assert result.dishes == []
        assert result.raw_response == "No dishes found"
        assert result.provider == "openai"
        assert result.processing_time == 0.5


class TestAIProvider:
    """Test cases for AIProvider abstract base class."""

    def test_cannot_instantiate_abstract_class(self):
        """Test that AIProvider cannot be instantiated directly."""
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            AIProvider()  # type: ignore

    def test_subclass_without_name_property_raises_error(self):
        """Test that subclass without name property cannot be instantiated."""

        class IncompleteProvider(AIProvider):
            def analyze_menu(self, image_data: bytes, mime_type: str) -> AnalysisResult:
                pass

            def is_available(self) -> bool:
                pass

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteProvider()  # type: ignore

    def test_subclass_without_analyze_menu_raises_error(self):
        """Test that subclass without analyze_menu cannot be instantiated."""

        class IncompleteProvider(AIProvider):
            @property
            def name(self) -> str:
                return "incomplete"

            def is_available(self) -> bool:
                pass

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteProvider()  # type: ignore

    def test_subclass_without_is_available_raises_error(self):
        """Test that subclass without is_available cannot be instantiated."""

        class IncompleteProvider(AIProvider):
            @property
            def name(self) -> str:
                return "incomplete"

            def analyze_menu(self, image_data: bytes, mime_type: str) -> AnalysisResult:
                pass

        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            IncompleteProvider()  # type: ignore

    def test_complete_subclass_can_be_instantiated(self):
        """Test that a complete subclass can be instantiated."""

        class CompleteProvider(AIProvider):
            @property
            def name(self) -> str:
                return "test-provider"

            def analyze_menu(self, image_data: bytes, mime_type: str) -> AnalysisResult:
                dish = Dish(
                    original_name="Test Dish",
                    japanese_name="テスト料理",
                    description="テスト用の料理",
                    spiciness=3,
                    sweetness=3,
                )
                return AnalysisResult(
                    dishes=[dish],
                    raw_response="test response",
                    provider=self.name,
                    processing_time=1.0,
                )

            def is_available(self) -> bool:
                return True

        provider = CompleteProvider()
        assert provider.name == "test-provider"
        assert provider.is_available() is True

        result = provider.analyze_menu(b"fake image data", "image/jpeg")
        assert len(result.dishes) == 1
        assert result.dishes[0].original_name == "Test Dish"
        assert result.provider == "test-provider"


class TestAIProviderExceptions:
    """Test cases for AI provider exception classes."""

    def test_ai_provider_error_can_be_raised(self):
        """Test that AIProviderError can be raised and caught."""
        with pytest.raises(AIProviderError, match="Generic AI provider error"):
            raise AIProviderError("Generic AI provider error")

    def test_api_key_missing_error_is_ai_provider_error(self):
        """Test that APIKeyMissingError is a subclass of AIProviderError."""
        assert issubclass(APIKeyMissingError, AIProviderError)

        with pytest.raises(AIProviderError):
            raise APIKeyMissingError("API key is missing")

    def test_api_call_error_is_ai_provider_error(self):
        """Test that APICallError is a subclass of AIProviderError."""
        assert issubclass(APICallError, AIProviderError)

        with pytest.raises(AIProviderError):
            raise APICallError("API call failed")

    def test_can_catch_specific_exception(self):
        """Test that specific exceptions can be caught separately."""
        try:
            raise APIKeyMissingError("No API key")
        except APIKeyMissingError as e:
            assert str(e) == "No API key"
        except AIProviderError:
            pytest.fail("Should have caught APIKeyMissingError")

    def test_can_catch_base_exception(self):
        """Test that base exception can catch all provider errors."""
        caught = False
        try:
            raise APICallError("API failed")
        except AIProviderError:
            caught = True

        assert caught is True


class TestClaudeProvider:
    """Test cases for ClaudeProvider."""

    def test_initialization_with_api_key(self):
        """Test ClaudeProvider initialization with API key."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-api-key"}):
            provider = ClaudeProvider()
            assert provider.api_key == "test-api-key"
            assert provider.client is not None
            assert provider.is_available() is True

    def test_initialization_without_api_key(self):
        """Test ClaudeProvider initialization without API key."""
        with patch.dict(os.environ, {}, clear=True):
            provider = ClaudeProvider()
            assert provider.api_key is None
            assert provider.client is None
            assert provider.is_available() is False

    def test_name_property(self):
        """Test that name property returns 'claude'."""
        with patch.dict(os.environ, {}, clear=True):
            provider = ClaudeProvider()
            assert provider.name == "claude"

    def test_build_prompt(self):
        """Test that _build_prompt returns appropriate prompt text."""
        with patch.dict(os.environ, {}, clear=True):
            provider = ClaudeProvider()
            prompt = provider._build_prompt()

            # Verify prompt contains key requirements
            assert "JSON" in prompt
            assert "original_name" in prompt
            assert "japanese_name" in prompt
            assert "spiciness" in prompt
            assert "sweetness" in prompt
            assert "ingredients" in prompt
            assert "allergens" in prompt
            assert "category" in prompt
            assert "price_range" in prompt

    def test_parse_response_valid_json(self):
        """Test parsing valid JSON response."""
        with patch.dict(os.environ, {}, clear=True):
            provider = ClaudeProvider()

            response_json = {
                "dishes": [
                    {
                        "original_name": "Pad Thai",
                        "japanese_name": "パッタイ",
                        "description": "米麺を使ったタイ風焼きそば",
                        "spiciness": 2,
                        "sweetness": 3,
                        "ingredients": ["米麺", "エビ", "卵"],
                        "allergens": ["甲殻類", "卵"],
                        "category": "main",
                        "price_range": "$$",
                    }
                ]
            }

            dishes = provider._parse_response(json.dumps(response_json))

            assert len(dishes) == 1
            assert dishes[0].original_name == "Pad Thai"
            assert dishes[0].japanese_name == "パッタイ"
            assert dishes[0].spiciness == 2
            assert dishes[0].sweetness == 3
            assert dishes[0].category == Category.MAIN
            assert dishes[0].price_range == PriceRange.MODERATE

    def test_parse_response_with_markdown_code_block(self):
        """Test parsing JSON wrapped in markdown code block."""
        with patch.dict(os.environ, {}, clear=True):
            provider = ClaudeProvider()

            response_json = {
                "dishes": [
                    {
                        "original_name": "Tom Yum",
                        "japanese_name": "トムヤム",
                        "description": "辛酸っぱいスープ",
                        "spiciness": 4,
                        "sweetness": 1,
                        "ingredients": ["エビ", "レモングラス"],
                        "allergens": ["甲殻類"],
                        "category": "appetizer",
                        "price_range": "$",
                    }
                ]
            }

            # Test with ```json wrapper
            response = f"```json\n{json.dumps(response_json)}\n```"
            dishes = provider._parse_response(response)

            assert len(dishes) == 1
            assert dishes[0].original_name == "Tom Yum"

            # Test with ``` wrapper
            response = f"```\n{json.dumps(response_json)}\n```"
            dishes = provider._parse_response(response)

            assert len(dishes) == 1
            assert dishes[0].original_name == "Tom Yum"

    def test_parse_response_invalid_json(self):
        """Test that invalid JSON raises APICallError."""
        with patch.dict(os.environ, {}, clear=True):
            provider = ClaudeProvider()

            with pytest.raises(APICallError, match="Failed to parse JSON response"):
                provider._parse_response("This is not JSON")

    def test_parse_response_missing_dishes_key(self):
        """Test that response without 'dishes' key raises APICallError."""
        with patch.dict(os.environ, {}, clear=True):
            provider = ClaudeProvider()

            response_json = {"menu": []}

            with pytest.raises(APICallError, match="Response must contain 'dishes' key"):
                provider._parse_response(json.dumps(response_json))

    def test_parse_response_empty_dishes(self):
        """Test that empty dishes list raises APICallError."""
        with patch.dict(os.environ, {}, clear=True):
            provider = ClaudeProvider()

            response_json = {"dishes": []}

            with pytest.raises(APICallError, match="No valid dishes found in response"):
                provider._parse_response(json.dumps(response_json))

    def test_parse_response_skips_invalid_dishes(self):
        """Test that invalid dishes are skipped but valid ones are kept."""
        with patch.dict(os.environ, {}, clear=True):
            provider = ClaudeProvider()

            response_json = {
                "dishes": [
                    {
                        # Invalid: missing required fields
                        "original_name": "Invalid Dish",
                    },
                    {
                        # Valid dish
                        "original_name": "Valid Dish",
                        "japanese_name": "有効な料理",
                        "description": "これは有効な料理です",
                        "spiciness": 3,
                        "sweetness": 3,
                        "ingredients": ["材料1"],
                        "allergens": [],
                        "category": "main",
                        "price_range": "$$",
                    },
                ]
            }

            dishes = provider._parse_response(json.dumps(response_json))

            # Should skip invalid dish and only return valid one
            assert len(dishes) == 1
            assert dishes[0].original_name == "Valid Dish"

    def test_analyze_menu_without_api_key(self):
        """Test that analyze_menu raises APIKeyMissingError without API key."""
        with patch.dict(os.environ, {}, clear=True):
            provider = ClaudeProvider()

            with pytest.raises(APIKeyMissingError, match="ANTHROPIC_API_KEY is not configured"):
                provider.analyze_menu(b"fake image data", "image/jpeg")

    def test_analyze_menu_image_size_exceeds_limit(self):
        """Test that analyze_menu raises APICallError when image size exceeds limit."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-api-key"}):
            provider = ClaudeProvider()

            # Create image data larger than MAX_IMAGE_SIZE (10MB)
            large_image_data = b"x" * (provider.MAX_IMAGE_SIZE + 1)

            with pytest.raises(
                APICallError, match="Image size .* bytes exceeds maximum .* bytes"
            ):
                provider.analyze_menu(large_image_data, "image/jpeg")

    @patch("anthropic.Anthropic")
    def test_analyze_menu_success(self, mock_anthropic_class):
        """Test successful menu analysis."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-api-key"}):
            # Setup mock
            mock_client = MagicMock()
            mock_anthropic_class.return_value = mock_client

            response_json = {
                "dishes": [
                    {
                        "original_name": "Green Curry",
                        "japanese_name": "グリーンカレー",
                        "description": "タイのグリーンカレー",
                        "spiciness": 4,
                        "sweetness": 2,
                        "ingredients": ["鶏肉", "ココナッツミルク", "バジル"],
                        "allergens": [],
                        "category": "main",
                        "price_range": "$$",
                    }
                ]
            }

            mock_response = MagicMock()
            mock_response.content = [MagicMock(text=json.dumps(response_json))]
            mock_client.messages.create.return_value = mock_response

            provider = ClaudeProvider()
            result = provider.analyze_menu(b"fake image data", "image/jpeg")

            # Verify result
            assert result.provider == "claude"
            assert len(result.dishes) == 1
            assert result.dishes[0].original_name == "Green Curry"
            assert result.processing_time > 0

            # Verify API call
            mock_client.messages.create.assert_called_once()
            call_args = mock_client.messages.create.call_args
            assert call_args[1]["model"] == "claude-3-5-sonnet-20241022"
            assert call_args[1]["max_tokens"] == 4096

    @patch("anthropic.Anthropic")
    def test_analyze_menu_api_error(self, mock_anthropic_class):
        """Test that API errors are properly handled."""
        import anthropic

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-api-key"}):
            mock_client = MagicMock()
            mock_anthropic_class.return_value = mock_client

            # Simulate API error with properly mocked anthropic.APIError
            api_error = anthropic.APIError(
                message="API Error",
                request=MagicMock(),
                body=None,
            )
            mock_client.messages.create.side_effect = api_error

            provider = ClaudeProvider()

            with pytest.raises(APICallError, match="Claude API call failed"):
                provider.analyze_menu(b"fake image data", "image/jpeg")
