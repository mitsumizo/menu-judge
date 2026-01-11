"""Claude API provider for menu analysis."""

from __future__ import annotations

import base64
import json
import logging
import time

import anthropic

from app.models.dish import Dish
from app.services.ai.base import (
    AIProvider,
    AnalysisResult,
    APICallError,
    APIKeyMissingError,
    InvalidMenuImageError,
)

logger = logging.getLogger(__name__)


class ClaudeProvider(AIProvider):
    """Claude APIを使用した画像解析プロバイダー"""

    MODEL = "claude-3-7-sonnet-20250219"
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB (matches CLAUDE.md spec)

    def __init__(self, api_key: str) -> None:
        """
        Initialize Claude provider.

        Args:
            api_key: Anthropic API key
        """
        super().__init__(api_key)
        if not self.api_key:
            raise APIKeyMissingError("API key is required")
        self.client = anthropic.Anthropic(api_key=self.api_key)

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
                max_tokens=4096,
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
        Build menu analysis prompt.

        Returns:
            Prompt text
        """
        return """This image is a restaurant menu. Please extract the following information for each dish in the image in JSON format.

For each dish, include the following information:
- original_name: Original dish name (as written on the menu)
- japanese_name: Dish name translated into English (if not already in English, translate it)
- description: Dish description (approximately 50 words in English)
- spiciness: Spiciness level (integer from 1 to 5, where 1=not spicy, 5=very spicy)
- sweetness: Sweetness level (integer from 1 to 5, where 1=not sweet, 5=very sweet)
- ingredients: List of main ingredients (in English)
- allergens: List of allergens (in English, e.g., eggs, dairy, wheat, soba, peanuts, shrimp, crab, etc.)
- category: Dish category (one of "appetizer", "main", "dessert", "beverage", "other")
- price_range: Price range (one of "$", "$$", "$$$", "$$$$", or null if cannot be determined)

Output in the following JSON format:
```json
{
  "dishes": [
    {
      "original_name": "Pad Thai",
      "japanese_name": "Pad Thai",
      "description": "Thai-style stir-fried rice noodles with shrimp, eggs, bean sprouts, and peanuts",
      "spiciness": 2,
      "sweetness": 3,
      "ingredients": ["rice noodles", "shrimp", "eggs", "bean sprouts", "peanuts"],
      "allergens": ["shellfish", "eggs", "nuts"],
      "category": "main",
      "price_range": "$$"
    }
  ]
}
```

Important notes:
- spiciness and sweetness must be integers from 1 to 5
- If information is unknown, use empty lists for ingredients or allergens
- If price_range cannot be determined, use null
- Do not include any text other than JSON
- Must output valid JSON format"""

    def _parse_response(self, response: str) -> list[Dish]:
        """
        Parse Claude response to list of Dish objects.

        Args:
            response: Claude API response text

        Returns:
            List of Dish objects

        Raises:
            APICallError: Failed to parse response
        """
        try:
            # Extract JSON from response (handle markdown code blocks)
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]  # Remove ```json
            if response.startswith("```"):
                response = response[3:]  # Remove ```
            if response.endswith("```"):
                response = response[:-3]  # Remove ```
            response = response.strip()

            # Parse JSON
            data = json.loads(response)

            # Validate structure
            if not isinstance(data, dict) or "dishes" not in data:
                raise ValueError("Response must contain 'dishes' key")

            dishes = []
            for dish_data in data["dishes"]:
                try:
                    dish = Dish.from_dict(dish_data)
                    dishes.append(dish)
                except Exception as e:
                    # Log error but continue with other dishes
                    logger.warning("Failed to parse dish: %s", e, exc_info=True)
                    continue

            if not dishes:
                raise InvalidMenuImageError(
                    "Could not detect menu from image. "
                    "Please verify that the image is a photo of a menu."
                )

            return dishes

        except InvalidMenuImageError:
            # Re-raise InvalidMenuImageError as-is
            raise
        except json.JSONDecodeError as e:
            raise APICallError(f"Failed to parse JSON response: {e}") from e
        except Exception as e:
            raise APICallError(f"Failed to parse response: {e}") from e
