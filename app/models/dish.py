"""料理データモデル"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Category(Enum):
    """料理のカテゴリ"""

    APPETIZER = "appetizer"
    MAIN = "main"
    DESSERT = "dessert"
    BEVERAGE = "beverage"
    OTHER = "other"


class PriceRange(Enum):
    """価格帯"""

    BUDGET = "$"
    MODERATE = "$$"
    EXPENSIVE = "$$$"
    LUXURY = "$$$$"


@dataclass
class Dish:
    """料理データモデル

    Attributes:
        original_name: 料理の原語名
        japanese_name: 料理の日本語名
        description: 料理の説明
        spiciness: 辛さレベル（1-5）
        sweetness: 甘さレベル（1-5）
        ingredients: 材料のリスト
        allergens: アレルゲンのリスト
        category: 料理のカテゴリ
        price_range: 価格帯
        image_url: 画像URL
        number: 料理の番号（メニュー画像での順序）
    """

    original_name: str
    japanese_name: str
    description: str
    spiciness: int  # 1-5
    sweetness: int  # 1-5
    ingredients: list[str] = field(default_factory=list)
    allergens: list[str] = field(default_factory=list)
    category: Category = Category.OTHER
    price_range: PriceRange | None = None
    image_url: str | None = None
    number: int | None = None

    def __post_init__(self) -> None:
        """バリデーション処理"""
        # 型チェック
        if not isinstance(self.spiciness, int):
            raise ValueError(f"spiciness must be an integer, got {type(self.spiciness).__name__}")
        if not isinstance(self.sweetness, int):
            raise ValueError(f"sweetness must be an integer, got {type(self.sweetness).__name__}")

        # 範囲チェック
        if not 1 <= self.spiciness <= 5:
            raise ValueError(f"spiciness must be 1-5, got {self.spiciness}")
        if not 1 <= self.sweetness <= 5:
            raise ValueError(f"sweetness must be 1-5, got {self.sweetness}")

    def to_dict(self) -> dict[str, Any]:
        """辞書に変換

        Returns:
            料理データの辞書表現
        """
        return {
            "original_name": self.original_name,
            "japanese_name": self.japanese_name,
            "description": self.description,
            "spiciness": self.spiciness,
            "sweetness": self.sweetness,
            "ingredients": self.ingredients,
            "allergens": self.allergens,
            "category": self.category.value,
            "price_range": self.price_range.value if self.price_range else None,
            "image_url": self.image_url,
            "number": self.number,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Dish":
        """辞書から生成

        Args:
            data: 料理データの辞書

        Returns:
            Dishインスタンス

        Raises:
            ValueError: 必須フィールドが欠けている場合
        """
        # 必須フィールドのチェック
        required_fields = ["original_name", "japanese_name", "description", "spiciness", "sweetness"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        # Enumの変換（無効な値はデフォルトにフォールバック）
        try:
            category = (
                Category(data["category"])
                if isinstance(data.get("category"), str)
                else data.get("category", Category.OTHER)
            )
        except (ValueError, KeyError):
            category = Category.OTHER

        try:
            price_range = PriceRange(data["price_range"]) if data.get("price_range") else None
        except (ValueError, KeyError):
            price_range = None

        return cls(
            original_name=data["original_name"],
            japanese_name=data["japanese_name"],
            description=data["description"],
            spiciness=data["spiciness"],
            sweetness=data["sweetness"],
            ingredients=data.get("ingredients", []),
            allergens=data.get("allergens", []),
            category=category,
            price_range=price_range,
            image_url=data.get("image_url"),
            number=data.get("number"),
        )
