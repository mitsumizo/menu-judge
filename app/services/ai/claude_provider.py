"""Claude API provider for menu analysis."""

from __future__ import annotations

import base64
import json
import os
import time

import anthropic

from app.models.dish import Dish
from app.services.ai.base import (
    AIProvider,
    AnalysisResult,
    APICallError,
    APIKeyMissingError,
)


class ClaudeProvider(AIProvider):
    """Claude APIを使用した画像解析プロバイダー"""

    MODEL = "claude-3-5-sonnet-20241022"

    def __init__(self) -> None:
        """Initialize Claude provider."""
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        self.client = None
        if self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)

    @property
    def name(self) -> str:
        """
        Get provider name.

        Returns:
            Provider name
        """
        return "claude"

    def is_available(self) -> bool:
        """
        Check if provider is available.

        Returns:
            True if provider is available, False otherwise
        """
        return self.api_key is not None

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
            APICallError: API call failed
        """
        if not self.is_available():
            raise APIKeyMissingError("ANTHROPIC_API_KEY is not configured")

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
        return """この画像はレストランのメニューです。画像内の各料理について、以下の情報をJSON形式で抽出してください。

各料理について以下の情報を含めてください:
- original_name: 料理の原語名（メニューに記載されている通り）
- japanese_name: 料理の日本語名（翻訳）
- description: 料理の説明（日本語で50文字程度）
- spiciness: 辛さレベル（1〜5の整数。1=辛くない、5=非常に辛い）
- sweetness: 甘さレベル（1〜5の整数。1=甘くない、5=非常に甘い）
- ingredients: 主な材料のリスト（日本語）
- allergens: アレルゲンのリスト（日本語。卵、乳製品、小麦、そば、落花生、えび、かに、etc.）
- category: 料理のカテゴリ（"appetizer", "main", "dessert", "beverage", "other"のいずれか）
- price_range: 価格帯（"$", "$$", "$$$", "$$$$"のいずれか。判断できない場合はnull）

以下のJSON形式で出力してください:
```json
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
    }
  ]
}
```

重要な注意事項:
- spiciness と sweetness は必ず1〜5の整数にしてください
- 情報が不明な場合、ingredients や allergens は空のリストにしてください
- price_range が判断できない場合は null にしてください
- JSON以外のテキストは含めないでください
- 必ず有効なJSON形式で出力してください"""

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
                    print(f"Warning: Failed to parse dish: {e}")
                    continue

            if not dishes:
                raise ValueError("No valid dishes found in response")

            return dishes

        except json.JSONDecodeError as e:
            raise APICallError(f"Failed to parse JSON response: {e}") from e
        except Exception as e:
            raise APICallError(f"Failed to parse response: {e}") from e
