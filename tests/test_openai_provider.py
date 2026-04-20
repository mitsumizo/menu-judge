"""Tests for OpenAIProvider (GPT-5.4 menu analysis).

パース共通ロジックは ``test_response_parser.py`` で検証するため、
ここでは OpenAI 固有の振る舞い（初期化・API 呼び出し形式・エラー変換）
に絞ってテストする。
"""

from __future__ import annotations

import json
import os
from unittest.mock import MagicMock, patch

import pytest

from app.services.ai.base import APICallError, APIKeyMissingError
from app.services.ai.factory import AIProviderFactory
from app.services.ai.openai_provider import OpenAIProvider


def _dish_payload() -> dict:
    return {
        "dishes": [
            {
                "original_name": "Green Curry",
                "translated_name": "グリーンカレー",
                "description": "タイのグリーンカレー",
                "spiciness": 4,
                "sweetness": 2,
                "ingredients": ["鶏肉", "ココナッツミルク"],
                "allergens": [],
                "category": "main",
                "number": 1,
            }
        ]
    }


def _mock_openai(mock_cls: MagicMock, response_text: str) -> MagicMock:
    """Return a MagicMock OpenAI client wired to return ``response_text``."""
    client = MagicMock()
    mock_cls.return_value = client
    message = MagicMock()
    message.content = response_text
    client.chat.completions.create.return_value = MagicMock(choices=[MagicMock(message=message)])
    return client


class TestOpenAIProviderInit:
    def test_initialization_sets_fields(self):
        provider = OpenAIProvider(api_key="sk-test", language="ja")
        assert provider.api_key == "sk-test"
        assert provider.language == "ja"
        assert provider.client is not None

    def test_default_language_is_en(self):
        assert OpenAIProvider(api_key="sk-test").language == "en"

    def test_empty_api_key_raises(self):
        with pytest.raises(APIKeyMissingError, match="API key is required"):
            OpenAIProvider(api_key="")

    def test_name_is_openai(self):
        with patch.dict(os.environ, {}, clear=True):
            assert OpenAIProvider(api_key="sk-test").name == "openai"


class TestOpenAIProviderPrompt:
    def test_prompt_includes_required_fields(self):
        prompt = OpenAIProvider(api_key="sk-test")._build_prompt()
        for key in ("JSON", "original_name", "translated_name", "spiciness",
                    "sweetness", "ingredients", "allergens", "category", "number"):
            assert key in prompt


class TestOpenAIProviderAnalyzeMenu:
    def test_rejects_oversized_image(self):
        provider = OpenAIProvider(api_key="sk-test")
        big = b"x" * (provider.MAX_IMAGE_SIZE + 1)
        with pytest.raises(APICallError, match="exceeds maximum"):
            provider.analyze_menu(big, "image/jpeg")

    @patch("app.services.ai.openai_provider.OpenAI")
    def test_success_returns_analysis_result(self, mock_openai_class):
        _mock_openai(mock_openai_class, json.dumps(_dish_payload()))

        provider = OpenAIProvider(api_key="sk-test")
        result = provider.analyze_menu(b"fake image", "image/jpeg")

        assert result.provider == "openai"
        assert result.processing_time > 0
        assert [d.original_name for d in result.dishes] == ["Green Curry"]

    @patch("app.services.ai.openai_provider.OpenAI")
    def test_sends_data_url_with_correct_mime_and_model(self, mock_openai_class):
        client = _mock_openai(mock_openai_class, json.dumps(_dish_payload()))

        OpenAIProvider(api_key="sk-test").analyze_menu(b"fake", "image/png")

        kwargs = client.chat.completions.create.call_args.kwargs
        assert kwargs["model"] == OpenAIProvider.MODEL
        assert kwargs["max_tokens"] == OpenAIProvider.MAX_TOKENS
        image_block = next(
            b for b in kwargs["messages"][0]["content"] if b["type"] == "image_url"
        )
        assert image_block["image_url"]["url"].startswith("data:image/png;base64,")

    @patch("app.services.ai.openai_provider.OpenAI")
    def test_wraps_openai_api_error(self, mock_openai_class):
        from openai import APIError

        client = MagicMock()
        mock_openai_class.return_value = client
        client.chat.completions.create.side_effect = APIError(
            message="boom", request=MagicMock(), body=None
        )

        with pytest.raises(APICallError, match="OpenAI API call failed"):
            OpenAIProvider(api_key="sk-test").analyze_menu(b"fake", "image/jpeg")

    @patch("app.services.ai.openai_provider.OpenAI")
    def test_wraps_unexpected_error(self, mock_openai_class):
        client = MagicMock()
        mock_openai_class.return_value = client
        client.chat.completions.create.side_effect = RuntimeError("unexpected")

        with pytest.raises(APICallError, match="Unexpected error"):
            OpenAIProvider(api_key="sk-test").analyze_menu(b"fake", "image/jpeg")


class TestOpenAIProviderFactoryRegistration:
    def test_factory_creates_openai(self):
        provider = AIProviderFactory.create(api_key="sk-test", provider_name="openai")
        assert isinstance(provider, OpenAIProvider)

    def test_openai_in_available_providers(self):
        assert "openai" in AIProviderFactory.available_providers()
