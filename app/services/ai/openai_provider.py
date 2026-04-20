"""OpenAI vision provider for menu analysis."""

from __future__ import annotations

import base64
import logging
import time

import openai
from openai import OpenAI

from app.services.ai.base import (
    AIProvider,
    AnalysisResult,
    APICallError,
    APIKeyMissingError,
)
from app.services.ai.prompt_builder import PromptBuilder
from app.services.ai.response_parser import parse_dishes

logger = logging.getLogger(__name__)

_NUMBER_FIELD_INSTRUCTION = """
- number: Dish order number in the menu image (integer, starting from 1)
  Assign numbers in reading order: top-to-bottom, then left-to-right for multi-column menus.
  Every dish MUST have a unique sequential number."""


class OpenAIProvider(AIProvider):
    """OpenAI ビジョン対応モデルを使った画像解析プロバイダー。

    デフォルトは GPT-5.4（2026年3月リリースのフラッグシップ）。
    画像理解・チャート推論・レイアウト把握が強化され、10Mピクセル超の画像も圧縮不要。
    """

    MODEL = "gpt-5.4"
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_TOKENS = 4096

    def __init__(self, api_key: str, language: str = "en") -> None:
        super().__init__(api_key, language)
        if not self.api_key:
            raise APIKeyMissingError("API key is required")
        self.client = OpenAI(api_key=self.api_key)
        self.prompt_builder = PromptBuilder(language)

    @property
    def name(self) -> str:
        return "openai"

    def analyze_menu(self, image_data: bytes, mime_type: str) -> AnalysisResult:
        if len(image_data) > self.MAX_IMAGE_SIZE:
            raise APICallError(
                f"Image size {len(image_data)} bytes exceeds maximum "
                f"{self.MAX_IMAGE_SIZE} bytes"
            )

        started = time.time()
        raw_response = self._call_api(image_data, mime_type)
        dishes = parse_dishes(raw_response)

        return AnalysisResult(
            dishes=dishes,
            raw_response=raw_response,
            provider=self.name,
            processing_time=time.time() - started,
        )

    def _call_api(self, image_data: bytes, mime_type: str) -> str:
        """Chat Completions エンドポイントを叩き、レスポンス本文だけ返す。"""
        image_base64 = base64.standard_b64encode(image_data).decode("utf-8")
        data_url = f"data:{mime_type};base64,{image_base64}"

        try:
            response = self.client.chat.completions.create(
                model=self.MODEL,
                max_tokens=self.MAX_TOKENS,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": self._build_prompt()},
                            {"type": "image_url", "image_url": {"url": data_url}},
                        ],
                    }
                ],
            )
        except openai.APIError as e:
            raise APICallError(f"OpenAI API call failed: {e}") from e
        except Exception as e:
            raise APICallError(f"Unexpected error during analysis: {e}") from e

        return response.choices[0].message.content or ""

    def _build_prompt(self) -> str:
        """多言語プロンプトに number フィールドの指示を差し込む。"""
        base = self.prompt_builder.build_menu_analysis_prompt()
        if "```json" in base:
            head, tail = base.split("```json", 1)
            return f"{head}{_NUMBER_FIELD_INSTRUCTION}\n\n```json{tail}"
        return base + _NUMBER_FIELD_INSTRUCTION
