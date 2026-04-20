"""Tests for OpenAIProvider (GPT-4V menu analysis)."""

from __future__ import annotations

import json
import os
from unittest.mock import MagicMock, patch

import pytest

from app.models.dish import Category
from app.services.ai.base import (
    APICallError,
    APIKeyMissingError,
    InvalidMenuImageError,
)
from app.services.ai.openai_provider import OpenAIProvider


def _build_dish_dict(name: str = "Pad Thai", number: int | None = 1) -> dict:
    """Build a minimal valid dish dict for response fixtures."""
    d = {
        "original_name": name,
        "translated_name": name,
        "description": f"desc {name}",
        "spiciness": 2,
        "sweetness": 3,
        "ingredients": ["x"],
        "allergens": [],
        "category": "main",
    }
    if number is not None:
        d["number"] = number
    return d


class TestOpenAIProviderInit:
    """OpenAIProvider initialization."""

    def test_initialization_with_api_key(self):
        provider = OpenAIProvider(api_key="sk-test-xyz")
        assert provider.api_key == "sk-test-xyz"
        assert provider.client is not None

    def test_initialization_without_api_key_raises(self):
        with pytest.raises(APIKeyMissingError, match="API key is required"):
            OpenAIProvider(api_key="")

    def test_name_property_returns_openai(self):
        with patch.dict(os.environ, {}, clear=True):
            provider = OpenAIProvider(api_key="sk-test-xyz")
            assert provider.name == "openai"

    def test_default_language(self):
        provider = OpenAIProvider(api_key="sk-test-xyz")
        assert provider.language == "en"

    def test_custom_language(self):
        provider = OpenAIProvider(api_key="sk-test-xyz", language="ja")
        assert provider.language == "ja"


class TestOpenAIProviderPrompt:
    """Prompt construction."""

    def test_build_prompt_includes_required_fields(self):
        with patch.dict(os.environ, {}, clear=True):
            provider = OpenAIProvider(api_key="sk-test-xyz")
            prompt = provider._build_prompt()

            assert "JSON" in prompt
            assert "original_name" in prompt
            assert "translated_name" in prompt
            assert "spiciness" in prompt
            assert "sweetness" in prompt
            assert "ingredients" in prompt
            assert "allergens" in prompt
            assert "category" in prompt


class TestOpenAIProviderParseResponse:
    """Response parsing."""

    def test_parse_valid_json(self):
        provider = OpenAIProvider(api_key="sk-test-xyz")
        payload = {"dishes": [_build_dish_dict("Pad Thai", 1)]}
        dishes = provider._parse_response(json.dumps(payload))

        assert len(dishes) == 1
        assert dishes[0].original_name == "Pad Thai"
        assert dishes[0].category == Category.MAIN

    def test_parse_markdown_fenced_json(self):
        provider = OpenAIProvider(api_key="sk-test-xyz")
        payload = {"dishes": [_build_dish_dict("Tom Yum", 1)]}
        fenced = f"```json\n{json.dumps(payload)}\n```"
        dishes = provider._parse_response(fenced)
        assert len(dishes) == 1
        assert dishes[0].original_name == "Tom Yum"

        fenced2 = f"```\n{json.dumps(payload)}\n```"
        dishes2 = provider._parse_response(fenced2)
        assert len(dishes2) == 1

    def test_parse_invalid_json_raises(self):
        provider = OpenAIProvider(api_key="sk-test-xyz")
        with pytest.raises(APICallError, match="Failed to parse JSON"):
            provider._parse_response("not json")

    def test_parse_missing_dishes_key_raises(self):
        provider = OpenAIProvider(api_key="sk-test-xyz")
        with pytest.raises(APICallError, match="'dishes' key"):
            provider._parse_response(json.dumps({"menu": []}))

    def test_parse_empty_dishes_raises_invalid_menu(self):
        provider = OpenAIProvider(api_key="sk-test-xyz")
        with pytest.raises(InvalidMenuImageError, match="Could not detect menu"):
            provider._parse_response(json.dumps({"dishes": []}))

    def test_parse_skips_invalid_dishes(self):
        provider = OpenAIProvider(api_key="sk-test-xyz")
        payload = {
            "dishes": [
                {"original_name": "Bad"},  # missing required fields
                _build_dish_dict("Good", 1),
            ]
        }
        dishes = provider._parse_response(json.dumps(payload))
        assert len(dishes) == 1
        assert dishes[0].original_name == "Good"

    def test_parse_reassigns_non_sequential_numbers(self):
        provider = OpenAIProvider(api_key="sk-test-xyz")
        payload = {
            "dishes": [
                _build_dish_dict("A", 1),
                _build_dish_dict("C", 3),  # gap at 2
                _build_dish_dict("D", 4),
            ]
        }
        dishes = provider._parse_response(json.dumps(payload))
        assert [d.number for d in dishes] == [1, 2, 3]
        assert [d.original_name for d in dishes] == ["A", "C", "D"]

    def test_parse_json_array_not_dict_raises(self):
        provider = OpenAIProvider(api_key="sk-test-xyz")
        with pytest.raises(APICallError, match="'dishes' key"):
            provider._parse_response(json.dumps(["not", "a", "dict"]))


class TestOpenAIProviderAnalyzeMenu:
    """analyze_menu integration with mocked OpenAI client."""

    def test_image_size_exceeds_limit_raises(self):
        provider = OpenAIProvider(api_key="sk-test-xyz")
        big = b"x" * (provider.MAX_IMAGE_SIZE + 1)
        with pytest.raises(APICallError, match="Image size .* exceeds maximum"):
            provider.analyze_menu(big, "image/jpeg")

    @patch("app.services.ai.openai_provider.OpenAI")
    def test_analyze_menu_success(self, mock_openai_class):
        payload = {"dishes": [_build_dish_dict("Green Curry", 1)]}
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps(payload)
        mock_client.chat.completions.create.return_value = mock_response

        provider = OpenAIProvider(api_key="sk-test-xyz")
        result = provider.analyze_menu(b"fake image", "image/jpeg")

        assert result.provider == "openai"
        assert len(result.dishes) == 1
        assert result.dishes[0].original_name == "Green Curry"
        assert result.processing_time > 0

        # Verify call signature
        mock_client.chat.completions.create.assert_called_once()
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs["model"] == OpenAIProvider.MODEL
        # Verify image is embedded as data URL with correct mime type
        messages = call_kwargs["messages"]
        content_blocks = messages[0]["content"]
        image_block = next(b for b in content_blocks if b["type"] == "image_url")
        assert image_block["image_url"]["url"].startswith("data:image/jpeg;base64,")

    @patch("app.services.ai.openai_provider.OpenAI")
    def test_analyze_menu_wraps_openai_api_error(self, mock_openai_class):
        from openai import APIError

        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = APIError(
            message="boom", request=MagicMock(), body=None
        )

        provider = OpenAIProvider(api_key="sk-test-xyz")
        with pytest.raises(APICallError, match="OpenAI API call failed"):
            provider.analyze_menu(b"fake", "image/jpeg")

    @patch("app.services.ai.openai_provider.OpenAI")
    def test_analyze_menu_wraps_unexpected_error(self, mock_openai_class):
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = RuntimeError("unexpected")

        provider = OpenAIProvider(api_key="sk-test-xyz")
        with pytest.raises(APICallError, match="Unexpected error"):
            provider.analyze_menu(b"fake", "image/jpeg")


class TestOpenAIProviderFactoryRegistration:
    """Factory integration."""

    def test_factory_creates_openai_provider(self):
        from app.services.ai.factory import AIProviderFactory

        provider = AIProviderFactory.create(api_key="sk-test-xyz", provider_name="openai")
        assert isinstance(provider, OpenAIProvider)
        assert provider.name == "openai"

    def test_openai_in_available_providers(self):
        from app.services.ai.factory import AIProviderFactory

        assert "openai" in AIProviderFactory.available_providers()
