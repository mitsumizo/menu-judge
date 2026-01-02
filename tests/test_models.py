"""Tests for Dish model."""

import pytest

from app.models.dish import Category, Dish, PriceRange


class TestDish:
    """Test cases for Dish model."""

    def test_dish_creation_with_all_fields(self):
        """Test creating a Dish with all fields specified."""
        dish = Dish(
            original_name="Pad Thai",
            japanese_name="パッタイ",
            description="米麺を使ったタイ風焼きそば",
            spiciness=2,
            sweetness=3,
            ingredients=["米麺", "エビ", "卵", "もやし", "ピーナッツ"],
            allergens=["甲殻類", "卵", "ナッツ"],
            category=Category.MAIN,
            price_range=PriceRange.MODERATE,
            image_url="https://example.com/pad-thai.jpg",
        )

        assert dish.original_name == "Pad Thai"
        assert dish.japanese_name == "パッタイ"
        assert dish.description == "米麺を使ったタイ風焼きそば"
        assert dish.spiciness == 2
        assert dish.sweetness == 3
        assert dish.ingredients == ["米麺", "エビ", "卵", "もやし", "ピーナッツ"]
        assert dish.allergens == ["甲殻類", "卵", "ナッツ"]
        assert dish.category == Category.MAIN
        assert dish.price_range == PriceRange.MODERATE
        assert dish.image_url == "https://example.com/pad-thai.jpg"

    def test_dish_creation_with_default_values(self):
        """Test creating a Dish with default values."""
        dish = Dish(
            original_name="Simple Dish",
            japanese_name="シンプル料理",
            description="説明",
            spiciness=1,
            sweetness=1,
        )

        assert dish.ingredients == []
        assert dish.allergens == []
        assert dish.category == Category.OTHER
        assert dish.price_range is None
        assert dish.image_url is None

    def test_spiciness_validation_below_range(self):
        """Test that spiciness below 1 raises ValueError."""
        with pytest.raises(ValueError, match="spiciness must be 1-5, got 0"):
            Dish(
                original_name="Too Mild",
                japanese_name="辛くない",
                description="辛さゼロ",
                spiciness=0,
                sweetness=3,
            )

    def test_spiciness_validation_above_range(self):
        """Test that spiciness above 5 raises ValueError."""
        with pytest.raises(ValueError, match="spiciness must be 1-5, got 6"):
            Dish(
                original_name="Too Spicy",
                japanese_name="辛すぎ",
                description="辛さ6",
                spiciness=6,
                sweetness=3,
            )

    def test_sweetness_validation_below_range(self):
        """Test that sweetness below 1 raises ValueError."""
        with pytest.raises(ValueError, match="sweetness must be 1-5, got 0"):
            Dish(
                original_name="Not Sweet",
                japanese_name="甘くない",
                description="甘さゼロ",
                spiciness=3,
                sweetness=0,
            )

    def test_sweetness_validation_above_range(self):
        """Test that sweetness above 5 raises ValueError."""
        with pytest.raises(ValueError, match="sweetness must be 1-5, got 6"):
            Dish(
                original_name="Too Sweet",
                japanese_name="甘すぎ",
                description="甘さ6",
                spiciness=3,
                sweetness=6,
            )

    def test_spiciness_validation_at_boundaries(self):
        """Test that spiciness at boundaries (1 and 5) are valid."""
        dish_min = Dish(
            original_name="Mild",
            japanese_name="マイルド",
            description="辛さ1",
            spiciness=1,
            sweetness=3,
        )
        assert dish_min.spiciness == 1

        dish_max = Dish(
            original_name="Very Spicy",
            japanese_name="激辛",
            description="辛さ5",
            spiciness=5,
            sweetness=3,
        )
        assert dish_max.spiciness == 5

    def test_sweetness_validation_at_boundaries(self):
        """Test that sweetness at boundaries (1 and 5) are valid."""
        dish_min = Dish(
            original_name="Not Sweet",
            japanese_name="甘さ控えめ",
            description="甘さ1",
            spiciness=3,
            sweetness=1,
        )
        assert dish_min.sweetness == 1

        dish_max = Dish(
            original_name="Very Sweet",
            japanese_name="激甘",
            description="甘さ5",
            spiciness=3,
            sweetness=5,
        )
        assert dish_max.sweetness == 5

    def test_spiciness_type_validation(self):
        """Test that spiciness must be an integer."""
        with pytest.raises(ValueError, match="spiciness must be an integer"):
            Dish(
                original_name="Invalid Type",
                japanese_name="無効な型",
                description="辛さが文字列",
                spiciness=3.5,  # type: ignore
                sweetness=3,
            )

    def test_sweetness_type_validation(self):
        """Test that sweetness must be an integer."""
        with pytest.raises(ValueError, match="sweetness must be an integer"):
            Dish(
                original_name="Invalid Type",
                japanese_name="無効な型",
                description="甘さが文字列",
                spiciness=3,
                sweetness="3",  # type: ignore
            )

    def test_to_dict(self):
        """Test converting Dish to dictionary."""
        dish = Dish(
            original_name="Pad Thai",
            japanese_name="パッタイ",
            description="米麺を使ったタイ風焼きそば",
            spiciness=2,
            sweetness=3,
            ingredients=["米麺", "エビ"],
            allergens=["甲殻類"],
            category=Category.MAIN,
            price_range=PriceRange.MODERATE,
            image_url="https://example.com/pad-thai.jpg",
        )

        result = dish.to_dict()

        assert result == {
            "original_name": "Pad Thai",
            "japanese_name": "パッタイ",
            "description": "米麺を使ったタイ風焼きそば",
            "spiciness": 2,
            "sweetness": 3,
            "ingredients": ["米麺", "エビ"],
            "allergens": ["甲殻類"],
            "category": "main",
            "price_range": "$$",
            "image_url": "https://example.com/pad-thai.jpg",
            "number": None,
        }

    def test_to_dict_with_none_values(self):
        """Test to_dict with None values."""
        dish = Dish(
            original_name="Simple",
            japanese_name="シンプル",
            description="説明",
            spiciness=1,
            sweetness=1,
        )

        result = dish.to_dict()

        assert result["price_range"] is None
        assert result["image_url"] is None

    def test_from_dict(self):
        """Test creating Dish from dictionary."""
        data = {
            "original_name": "Pad Thai",
            "japanese_name": "パッタイ",
            "description": "米麺を使ったタイ風焼きそば",
            "spiciness": 2,
            "sweetness": 3,
            "ingredients": ["米麺", "エビ"],
            "allergens": ["甲殻類"],
            "category": "main",
            "price_range": "$$",
            "image_url": "https://example.com/pad-thai.jpg",
        }

        dish = Dish.from_dict(data)

        assert dish.original_name == "Pad Thai"
        assert dish.japanese_name == "パッタイ"
        assert dish.description == "米麺を使ったタイ風焼きそば"
        assert dish.spiciness == 2
        assert dish.sweetness == 3
        assert dish.ingredients == ["米麺", "エビ"]
        assert dish.allergens == ["甲殻類"]
        assert dish.category == Category.MAIN
        assert dish.price_range == PriceRange.MODERATE
        assert dish.image_url == "https://example.com/pad-thai.jpg"

    def test_from_dict_with_missing_optional_fields(self):
        """Test from_dict with missing optional fields."""
        data = {
            "original_name": "Simple",
            "japanese_name": "シンプル",
            "description": "説明",
            "spiciness": 1,
            "sweetness": 1,
        }

        dish = Dish.from_dict(data)

        assert dish.ingredients == []
        assert dish.allergens == []
        assert dish.category == Category.OTHER
        assert dish.price_range is None
        assert dish.image_url is None

    def test_to_dict_from_dict_roundtrip(self):
        """Test roundtrip conversion: Dish -> dict -> Dish."""
        original = Dish(
            original_name="Pad Thai",
            japanese_name="パッタイ",
            description="米麺を使ったタイ風焼きそば",
            spiciness=2,
            sweetness=3,
            ingredients=["米麺", "エビ", "卵"],
            allergens=["甲殻類", "卵"],
            category=Category.MAIN,
            price_range=PriceRange.MODERATE,
            image_url="https://example.com/pad-thai.jpg",
        )

        # to_dict -> from_dict
        data = original.to_dict()
        restored = Dish.from_dict(data)

        # Verify all fields match
        assert restored.original_name == original.original_name
        assert restored.japanese_name == original.japanese_name
        assert restored.description == original.description
        assert restored.spiciness == original.spiciness
        assert restored.sweetness == original.sweetness
        assert restored.ingredients == original.ingredients
        assert restored.allergens == original.allergens
        assert restored.category == original.category
        assert restored.price_range == original.price_range
        assert restored.image_url == original.image_url
        assert restored.number == original.number

    def test_from_dict_with_enum_objects(self):
        """Test from_dict can handle Enum objects in addition to strings."""
        data = {
            "original_name": "Test",
            "japanese_name": "テスト",
            "description": "説明",
            "spiciness": 1,
            "sweetness": 1,
            "category": Category.APPETIZER,
            "price_range": PriceRange.BUDGET,
        }

        dish = Dish.from_dict(data)

        assert dish.category == Category.APPETIZER
        assert dish.price_range == PriceRange.BUDGET

    def test_from_dict_missing_required_fields(self):
        """Test from_dict raises ValueError when required fields are missing."""
        # Missing original_name
        data = {
            "japanese_name": "テスト",
            "description": "説明",
            "spiciness": 1,
            "sweetness": 1,
        }
        with pytest.raises(ValueError, match="Missing required fields: original_name"):
            Dish.from_dict(data)

    def test_from_dict_missing_multiple_required_fields(self):
        """Test from_dict raises ValueError with all missing fields listed."""
        # Missing multiple fields
        data = {
            "original_name": "Test",
        }
        with pytest.raises(
            ValueError,
            match="Missing required fields: japanese_name, description, spiciness, sweetness",
        ):
            Dish.from_dict(data)


class TestCategory:
    """Test cases for Category enum."""

    def test_category_values(self):
        """Test that all category values are defined correctly."""
        assert Category.APPETIZER.value == "appetizer"
        assert Category.MAIN.value == "main"
        assert Category.DESSERT.value == "dessert"
        assert Category.BEVERAGE.value == "beverage"
        assert Category.OTHER.value == "other"

    def test_category_from_string(self):
        """Test creating Category from string value."""
        assert Category("appetizer") == Category.APPETIZER
        assert Category("main") == Category.MAIN
        assert Category("dessert") == Category.DESSERT
        assert Category("beverage") == Category.BEVERAGE
        assert Category("other") == Category.OTHER


class TestPriceRange:
    """Test cases for PriceRange enum."""

    def test_price_range_values(self):
        """Test that all price range values are defined correctly."""
        assert PriceRange.BUDGET.value == "$"
        assert PriceRange.MODERATE.value == "$$"
        assert PriceRange.EXPENSIVE.value == "$$$"
        assert PriceRange.LUXURY.value == "$$$$"

    def test_price_range_from_string(self):
        """Test creating PriceRange from string value."""
        assert PriceRange("$") == PriceRange.BUDGET
        assert PriceRange("$$") == PriceRange.MODERATE
        assert PriceRange("$$$") == PriceRange.EXPENSIVE
        assert PriceRange("$$$$") == PriceRange.LUXURY
