"""Tests for AI provider base classes."""

import pytest

from app.models.dish import Category, Dish, PriceRange
from app.services.ai.base import (
    AIProvider,
    AIProviderError,
    AnalysisResult,
    APICallError,
    APIKeyMissingError,
)


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
