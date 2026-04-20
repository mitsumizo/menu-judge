"""Claude API provider for menu analysis."""

from __future__ import annotations

import base64
import logging
import time
from typing import Literal, cast

import anthropic

from app.models.dish import Dish
from app.services.ai.base import (
    AIProvider,
    AnalysisResult,
    APICallError,
    APIKeyMissingError,
)
from app.services.ai.prompt_builder import PromptBuilder
from app.services.ai.response_parser import parse_dishes

logger = logging.getLogger(__name__)


class ClaudeProvider(AIProvider):
    """Claude APIを使用した画像解析プロバイダー"""

    MODEL = "claude-sonnet-4-6"
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB (matches CLAUDE.md spec)

    def __init__(self, api_key: str, language: str = "en") -> None:
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

            # Call Claude API — mime_type validated against ALLOWED_MIME_TYPES at the route layer.
            messages: list[anthropic.types.MessageParam] = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": cast(
                                    Literal[
                                        "image/jpeg",
                                        "image/png",
                                        "image/gif",
                                        "image/webp",
                                    ],
                                    mime_type,
                                ),
                                "data": image_base64,
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ]
            response = self.client.messages.create(
                model=self.MODEL,
                max_tokens=8192,
                messages=messages,
            )

            # Parse response — Claude returns TextBlock for our text-only prompt
            text_block = cast(anthropic.types.TextBlock, response.content[0])
            raw_response = text_block.text
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
        """Parse Claude response into a list of Dish objects."""
        return parse_dishes(response)
