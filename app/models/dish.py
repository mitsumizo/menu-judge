"""Dish data model for menu analysis results."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Category(Enum):
    """Dish category."""

    APPETIZER = "appetizer"
    MAIN = "main"
    DESSERT = "dessert"
    BEVERAGE = "beverage"
    OTHER = "other"


class PriceRange(Enum):
    """Price range indicator."""

    BUDGET = "$"
    MODERATE = "$$"
    EXPENSIVE = "$$$"
    LUXURY = "$$$$"


@dataclass
class Dish:
    """
    Dish data model representing a menu item.

    Attributes:
        original_name: Original name of the dish
        japanese_name: Japanese translation of the dish name
        description: Description of the dish
        spiciness: Spiciness level (1-5)
        sweetness: Sweetness level (1-5)
        ingredients: List of ingredients
        allergens: List of allergens
        category: Dish category
        price_range: Price range indicator
        image_url: Optional image URL
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

    def __post_init__(self) -> None:
        """Validate spiciness and sweetness values."""
        # Type validation
        if not isinstance(self.spiciness, int):
            raise ValueError(f"spiciness must be an integer, got {type(self.spiciness).__name__}")
        if not isinstance(self.sweetness, int):
            raise ValueError(f"sweetness must be an integer, got {type(self.sweetness).__name__}")

        # Range validation
        if not 1 <= self.spiciness <= 5:
            raise ValueError(f"spiciness must be 1-5, got {self.spiciness}")
        if not 1 <= self.sweetness <= 5:
            raise ValueError(f"sweetness must be 1-5, got {self.sweetness}")

    def to_dict(self) -> dict[str, Any]:
        """
        Convert Dish to dictionary.

        Returns:
            Dictionary representation of the Dish
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
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Dish:
        """
        Create Dish from dictionary.

        Args:
            data: Dictionary containing dish data

        Returns:
            Dish instance

        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Validate required fields
        required_fields = [
            "original_name",
            "japanese_name",
            "description",
            "spiciness",
            "sweetness",
        ]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        category = data.get("category", "other")
        if isinstance(category, str):
            category = Category(category)

        price_range = data.get("price_range")
        if isinstance(price_range, str):
            price_range = PriceRange(price_range)

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
        )
