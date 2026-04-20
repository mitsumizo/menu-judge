"""AIビジョンプロバイダー共通のレスポンス解析ヘルパー。

Claude / OpenAI など複数プロバイダーが同じ JSON 契約（``{"dishes": [...]}``）で
料理情報を返すため、パース・番号正規化・フェンス除去は共通化している。
"""

from __future__ import annotations

import json
import logging
from dataclasses import replace

from app.models.dish import Dish
from app.services.ai.base import APICallError, InvalidMenuImageError

logger = logging.getLogger(__name__)


def parse_dishes(response: str) -> list[Dish]:
    """AI レスポンス本文から Dish のリストを生成する。

    Markdown コードフェンス除去 → JSON パース → Dish 変換（不正な dish は
    スキップ）→ 番号正規化までを 1 関数で担う。

    Args:
        response: AI からの生レスポンス本文

    Returns:
        有効な Dish のリスト（番号は 1-indexed の連番に正規化済み）

    Raises:
        APICallError: JSON として解釈不能、または ``dishes`` キー欠落
        InvalidMenuImageError: 有効な dish が 1 件も得られない
    """
    cleaned = _strip_markdown_fences(response)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise APICallError(f"Failed to parse JSON response: {e}") from e

    if not isinstance(data, dict) or "dishes" not in data:
        raise APICallError("Response must contain 'dishes' key")

    dishes: list[Dish] = []
    for item in data["dishes"]:
        try:
            dishes.append(Dish.from_dict(item))
        except (ValueError, KeyError, TypeError) as e:
            logger.warning("Failed to parse dish: %s", e, exc_info=True)

    if not dishes:
        raise InvalidMenuImageError(
            "Could not detect menu from image. "
            "Please verify that the image is a photo of a menu."
        )

    return _normalize_dish_numbers(dishes)


def _strip_markdown_fences(response: str) -> str:
    """先頭/末尾の markdown コードフェンスを除去した本文を返す。"""
    cleaned = response.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()


def _normalize_dish_numbers(dishes: list[Dish]) -> list[Dish]:
    """番号の欠損・重複・非連続を検出し、必要ならインデックス順で振り直す。

    完全な連番（順不同可）の場合は number 順にソートして返す。
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
