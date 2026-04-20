"""Claude API provider for menu analysis."""

from __future__ import annotations

import base64
import json
import logging
import time
from dataclasses import replace

import anthropic

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


class ClaudeProvider(AIProvider):
    """Claude APIを使用した画像解析プロバイダー"""

    MODEL = "claude-3-7-sonnet-20250219"
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB (matches CLAUDE.md spec)

    def __init__(self, api_key: str, language: str = 'en') -> None:
        """
        Initialize Claude provider.

        Args:
            api_key: Anthropic API key
            language: Language code for responses ('en' or 'ja')
        """
        super().__init__(api_key, language)
        if not self.api_key:
            raise APIKeyMissingError("API key is required")
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.prompt_builder = PromptBuilder(language)

    @property
    def name(self) -> str:
        """
        Get provider name.

        Returns:
            Provider name
        """
        return "claude"

    def analyze_menu(self, image_data: bytes, mime_type: str) -> AnalysisResult:
        """
        Analyze menu image and return dish information.

        Args:
            image_data: Image binary data
            mime_type: Image MIME type (image/jpeg, image/png, etc.)

        Returns:
            AnalysisResult: Analysis result

        Raises:
            APIKeyMissingError: API key is not configured
            APICallError: API call failed or image size exceeds limit
        """
        # Validate image size
        if len(image_data) > self.MAX_IMAGE_SIZE:
            raise APICallError(
                f"Image size {len(image_data)} bytes exceeds maximum "
                f"{self.MAX_IMAGE_SIZE} bytes"
            )

        start_time = time.time()

        try:
            # Encode image to base64
            image_base64 = base64.standard_b64encode(image_data).decode("utf-8")

            # Build prompt
            prompt = self._build_prompt()

            # Call Claude API
            response = self.client.messages.create(
                model=self.MODEL,
                max_tokens=8192,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": mime_type,
                                    "data": image_base64,
                                },
                            },
                            {"type": "text", "text": prompt},
                        ],
                    }
                ],
            )

            # Parse response
            raw_response = response.content[0].text
            dishes = self._parse_response(raw_response)

            processing_time = time.time() - start_time

            return AnalysisResult(
                dishes=dishes,
                raw_response=raw_response,
                provider=self.name,
                processing_time=processing_time,
            )

        except anthropic.APIError as e:
            raise APICallError(f"Claude API call failed: {e}") from e
        except Exception as e:
            raise APICallError(f"Unexpected error during analysis: {e}") from e

    def _build_prompt(self) -> str:
        """
        Build menu analysis prompt using the multilingual prompt builder.

        Returns:
            Prompt text in the selected language
        """
        # Get base prompt from multilingual prompt builder
        base_prompt = self.prompt_builder.build_menu_analysis_prompt()

        # Add number field instructions
        number_instruction = """
- number: Dish order number in the menu image (integer, starting from 1)
  Assign numbers in reading order: top-to-bottom, then left-to-right for multi-column menus.
  Every dish MUST have a unique sequential number."""

        # Add bounding_box field instructions with improved guidance
        bounding_box_instruction = """
- bounding_box: The location of the dish entry in the menu image (REQUIRED for each dish)
  IMPORTANT: Think of the image as a 1.0 x 1.0 coordinate system where:
  - (0, 0) is the TOP-LEFT corner of the image
  - (1, 1) is the BOTTOM-RIGHT corner of the image

  - x: X coordinate of the LEFT edge of the dish entry (0.0 to 1.0)
  - y: Y coordinate of the TOP edge of the dish entry (0.0 to 1.0)
  - width: Width of the bounding box (0.0 to 1.0)
  - height: Height of the bounding box (0.0 to 1.0)

  CRITICAL guidelines for bounding_box:
  1. The bounding box should tightly enclose ONLY the dish name and its price/description text
  2. Analyze the vertical position of each dish in the menu from TOP to BOTTOM
     - First dish on the page should have a smaller y value (closer to 0)
     - Last dish on the page should have a larger y value (closer to 1)
  3. For a typical single-column menu:
     - x is usually around 0.05-0.15 (dishes start near the left edge with some margin)
     - width is usually around 0.7-0.9 (dishes span most of the width)
  4. For a multi-column menu:
     - Left column: x around 0.02-0.1
     - Right column: x around 0.5-0.55
  5. Height should match the actual text height of that dish entry (usually 0.03-0.1)
  6. ALWAYS provide bounding_box coordinates - do not set to null unless truly impossible"""

        extra_instructions = number_instruction + bounding_box_instruction

        # Insert instructions before the output format section
        if "```json" in base_prompt:
            parts = base_prompt.split("```json")
            return parts[0] + extra_instructions + "\n\n```json" + parts[1]
        return base_prompt + extra_instructions

    def _parse_response(self, response: str) -> list[Dish]:
        """
        Parse Claude response to list of Dish objects.

        Args:
            response: Claude API response text

        Returns:
            List of Dish objects

        Raises:
            APICallError: Failed to parse response
            InvalidMenuImageError: No dishes could be detected
        """
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

        dishes = self._normalize_dish_numbers(dishes)
        return dishes

    @staticmethod
    def _normalize_dish_numbers(dishes: list[Dish]) -> list[Dish]:
        """料理番号の欠損・重複・非連続を検出し、必要なら連番を振り直す。

        AIが番号を省略・重複・スキップした場合や、無効dishのスキップで
        番号が飛んだ場合（例: [1, 3, 4]）、インデックス順で連番を再割当て
        する。完全な連番（順不同可）の場合はnumber順にソートしてから返す。

        Args:
            dishes: AIから返された料理リスト

        Returns:
            numberが正規化された料理リスト（イミュータブル: 新しいリストを返す）
        """
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
        """Strip markdown code fences from Claude response text."""
        cleaned = response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        return cleaned.strip()
