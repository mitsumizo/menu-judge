"""料理データモデル"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


@dataclass
class BoundingBox:
    """バウンディングボックス（正規化座標0-1スケール）

    Attributes:
        x: 左端のX座標（0-1）
        y: 上端のY座標（0-1）
        width: 幅（0-1）
        height: 高さ（0-1）
    """

    x: float
    y: float
    width: float
    height: float

    def __post_init__(self) -> None:
        """バリデーション処理"""
        for attr in ["x", "y", "width", "height"]:
            val = getattr(self, attr)
            if not isinstance(val, (int, float)):
                raise TypeError(f"{attr} must be a number, got {type(val).__name__}")
            if not (0 <= val <= 1):
                raise ValueError(f"{attr} must be between 0 and 1, got {val}")

    def to_dict(self) -> dict[str, float]:
        """辞書に変換"""
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BoundingBox":
        """辞書から生成"""
        required = ["x", "y", "width", "height"]
        missing = [f for f in required if f not in data]
        if missing:
            raise ValueError(f"Missing required fields: {', '.join(missing)}")
        return cls(
            x=float(data["x"]),
            y=float(data["y"]),
            width=float(data["width"]),
            height=float(data["height"]),
        )


class Category(Enum):
    """料理のカテゴリ"""

    APPETIZER = "appetizer"
    MAIN = "main"
    DESSERT = "dessert"
    BEVERAGE = "beverage"
    OTHER = "other"


@dataclass
class Dish:
    """料理データモデル

    Attributes:
        original_name: 料理の原語名
        translated_name: 料理の翻訳名（選択言語に応じた翻訳）
        description: 料理の説明
        spiciness: 辛さレベル（1-5）
        sweetness: 甘さレベル（1-5）
        ingredients: 材料のリスト
        allergens: アレルゲンのリスト
        category: 料理のカテゴリ
        image_url: 画像URL
        number: 料理の番号（メニュー画像での順序）
        bounding_box: メニュー画像上の位置（正規化座標）
    """

    original_name: str
    translated_name: str
    description: str
    spiciness: int  # 1-5
    sweetness: int  # 1-5
    ingredients: list[str] = field(default_factory=list)
    allergens: list[str] = field(default_factory=list)
    category: Category = Category.OTHER
    image_url: str | None = None
    number: int | None = None
    bounding_box: BoundingBox | None = None

    def __post_init__(self) -> None:
        """バリデーション処理"""
        # 型チェック
        if not isinstance(self.spiciness, int):
            raise TypeError(f"spiciness must be an integer, got {type(self.spiciness).__name__}")
        if not isinstance(self.sweetness, int):
            raise TypeError(f"sweetness must be an integer, got {type(self.sweetness).__name__}")

        # 範囲チェック
        if not 1 <= self.spiciness <= 5:
            raise ValueError(f"spiciness must be 1-5, got {self.spiciness}")
        if not 1 <= self.sweetness <= 5:
            raise ValueError(f"sweetness must be 1-5, got {self.sweetness}")

        # numberの検証（Noneは許容、指定時は1以上の整数）
        if self.number is not None:
            if not isinstance(self.number, int) or isinstance(self.number, bool):
                raise TypeError(f"number must be an integer, got {type(self.number).__name__}")
            if self.number < 1:
                raise ValueError(f"number must be >= 1, got {self.number}")

    def to_dict(self) -> dict[str, Any]:
        """辞書に変換

        Returns:
            料理データの辞書表現
        """
        return {
            "original_name": self.original_name,
            "translated_name": self.translated_name,
            "description": self.description,
            "spiciness": self.spiciness,
            "sweetness": self.sweetness,
            "ingredients": self.ingredients,
            "allergens": self.allergens,
            "category": self.category.value,
            "image_url": self.image_url,
            "number": self.number,
            "bounding_box": self.bounding_box.to_dict() if self.bounding_box else None,
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
        required_fields = [
            "original_name",
            "translated_name",
            "description",
            "spiciness",
            "sweetness",
        ]
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

        # BoundingBoxの変換（無効な値はNoneにフォールバック）
        bounding_box = None
        if data.get("bounding_box"):
            try:
                bounding_box = BoundingBox.from_dict(data["bounding_box"])
            except (ValueError, KeyError):
                bounding_box = None

        return cls(
            original_name=data["original_name"],
            translated_name=data["translated_name"],
            description=data["description"],
            spiciness=data["spiciness"],
            sweetness=data["sweetness"],
            ingredients=data.get("ingredients", []),
            allergens=data.get("allergens", []),
            category=category,
            image_url=data.get("image_url"),
            number=data.get("number"),
            bounding_box=bounding_box,
        )
