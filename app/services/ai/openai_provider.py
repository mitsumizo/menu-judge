"""OpenAI vision provider for menu analysis."""

from __future__ import annotations

import base64
import json
import logging
import time
from dataclasses import replace

import openai
from openai import OpenAI

from app.models.dish import Dish
from app.services.ai.base import (
    AIProvider,
    AnalysisResult,
    APICallError,
    APIKeyMissingError,
    InvalidMenuImageError,
)
from app.services.ai.prompt_builder import PromptBuilder

logger = logging.getLogger(__name__)


class OpenAIProvider(AIProvider):
    """OpenAIのビジョン対応モデルを使用した画像解析プロバイダー。

    デフォルトでは GPT-5.4 を使用（2026年3月リリースのフラッグシップ）。
    画像理解・チャート推論・レイアウト把握が強化され、10Mピクセル超の画像も圧縮不要。
    """

    MODEL = "gpt-5.4"
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_TOKENS = 4096

    def __init__(self, api_key: str, language: str = "en") -> None:
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key
            language: Language code for responses ('en' or 'ja')
        """
        super().__init__(api_key, language)
        if not self.api_key:
            raise APIKeyMissingError("API key is required")
        self.client = OpenAI(api_key=self.api_key)
        self.prompt_builder = PromptBuilder(language)

    @property
    def name(self) -> str:
        """Return provider name."""
        return "openai"

    def analyze_menu(self, image_data: bytes, mime_type: str) -> AnalysisResult:
        """
        Analyze menu image via GPT-4V.

        Args:
            image_data: Image binary data
            mime_type: Image MIME type (validated at route layer)

        Returns:
            AnalysisResult: Parsed analysis result

        Raises:
            APICallError: Image too large, API failure, or parsing error
            InvalidMenuImageError: No dishes detected
        """
        if len(image_data) > self.MAX_IMAGE_SIZE:
            raise APICallError(
                f"Image size {len(image_data)} bytes exceeds maximum "
                f"{self.MAX_IMAGE_SIZE} bytes"
            )

        start_time = time.time()

        try:
            image_base64 = base64.standard_b64encode(image_data).decode("utf-8")
            data_url = f"data:{mime_type};base64,{image_base64}"
            prompt = self._build_prompt()

            response = self.client.chat.completions.create(
                model=self.MODEL,
                max_tokens=self.MAX_TOKENS,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": data_url},
                            },
                        ],
                    }
                ],
            )

            raw_response = response.choices[0].message.content or ""
            dishes = self._parse_response(raw_response)
            processing_time = time.time() - start_time

            return AnalysisResult(
                dishes=dishes,
                raw_response=raw_response,
                provider=self.name,
                processing_time=processing_time,
            )

        except InvalidMenuImageError:
            raise
        except APICallError:
            raise
        except openai.APIError as e:
            raise APICallError(f"OpenAI API call failed: {e}") from e
        except Exception as e:
            raise APICallError(f"Unexpected error during analysis: {e}") from e

    def _build_prompt(self) -> str:
        """Build menu analysis prompt using the shared multilingual builder."""
        base_prompt = self.prompt_builder.build_menu_analysis_prompt()

        number_instruction = """
- number: Dish order number in the menu image (integer, starting from 1)
  Assign numbers in reading order: top-to-bottom, then left-to-right for multi-column menus.
  Every dish MUST have a unique sequential number."""

        if "```json" in base_prompt:
            parts = base_prompt.split("```json")
            return parts[0] + number_instruction + "\n\n```json" + parts[1]
        return base_prompt + number_instruction

    def _parse_response(self, response: str) -> list[Dish]:
        """Parse GPT-4V JSON response into Dish list."""
        cleaned = self._strip_markdown_fences(response)

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise APICallError(f"Failed to parse JSON response: {e}") from e

        if not isinstance(data, dict) or "dishes" not in data:
            raise APICallError("Response must contain 'dishes' key")

        dishes: list[Dish] = []
        for dish_data in data["dishes"]:
            try:
                dishes.append(Dish.from_dict(dish_data))
            except (ValueError, KeyError, TypeError) as e:
                logger.warning("Failed to parse dish: %s", e, exc_info=True)
                continue

        if not dishes:
            raise InvalidMenuImageError(
                "Could not detect menu from image. "
                "Please verify that the image is a photo of a menu."
            )

        return self._normalize_dish_numbers(dishes)

    @staticmethod
    def _normalize_dish_numbers(dishes: list[Dish]) -> list[Dish]:
        """Reassign sequential numbers if missing/duplicate/non-sequential."""
        numbers = [d.number for d in dishes]
        expected = list(range(1, len(dishes) + 1))
        has_missing = any(n is None for n in numbers)
        is_sequential = not has_missing and sorted(numbers) == expected  # type: ignore[type-var]

        if not is_sequential:
            logger.warning(
                "Dish numbers invalid (numbers=%s); reassigning sequential numbers",
                numbers,
            )
            return [replace(d, number=i + 1) for i, d in enumerate(dishes)]

        return sorted(dishes, key=lambda d: d.number)  # type: ignore[arg-type,return-value]

    @staticmethod
    def _strip_markdown_fences(response: str) -> str:
        """Strip ```json / ``` fences from a response body."""
        cleaned = response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        return cleaned.strip()
