"""Dishデータモデルのテスト"""

import pytest

from app.models import Category, Dish, PriceRange


class TestDish:
    """Dishクラスのテスト"""

    def test_create_dish_with_valid_data(self) -> None:
        """正常なデータでDishインスタンスを作成"""
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

    def test_create_dish_with_defaults(self) -> None:
        """デフォルト値でDishインスタンスを作成"""
        dish = Dish(
            original_name="Simple Dish",
            japanese_name="シンプルな料理",
            description="シンプルな料理の説明",
            spiciness=1,
            sweetness=1,
        )

        assert dish.ingredients == []
        assert dish.allergens == []
        assert dish.category == Category.OTHER
        assert dish.price_range is None
        assert dish.image_url is None

    @pytest.mark.parametrize("spiciness", [0, -1, 6, 10])
    def test_spiciness_validation_fails(self, spiciness: int) -> None:
        """spiciness が範囲外の場合にエラーが発生"""
        with pytest.raises(ValueError, match=f"spiciness must be 1-5, got {spiciness}"):
            Dish(
                original_name="Test",
                japanese_name="テスト",
                description="テスト料理",
                spiciness=spiciness,
                sweetness=3,
            )

    @pytest.mark.parametrize("sweetness", [0, -1, 6, 10])
    def test_sweetness_validation_fails(self, sweetness: int) -> None:
        """sweetness が範囲外の場合にエラーが発生"""
        with pytest.raises(ValueError, match=f"sweetness must be 1-5, got {sweetness}"):
            Dish(
                original_name="Test",
                japanese_name="テスト",
                description="テスト料理",
                spiciness=3,
                sweetness=sweetness,
            )

    @pytest.mark.parametrize("spiciness,sweetness", [(1, 1), (3, 3), (5, 5)])
    def test_boundary_values(self, spiciness: int, sweetness: int) -> None:
        """境界値のテスト"""
        dish = Dish(
            original_name="Boundary Test",
            japanese_name="境界値テスト",
            description="境界値のテスト料理",
            spiciness=spiciness,
            sweetness=sweetness,
        )

        assert dish.spiciness == spiciness
        assert dish.sweetness == sweetness

    def test_to_dict(self) -> None:
        """to_dictメソッドのテスト"""
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

        assert result["original_name"] == "Pad Thai"
        assert result["japanese_name"] == "パッタイ"
        assert result["description"] == "米麺を使ったタイ風焼きそば"
        assert result["spiciness"] == 2
        assert result["sweetness"] == 3
        assert result["ingredients"] == ["米麺", "エビ"]
        assert result["allergens"] == ["甲殻類"]
        assert result["category"] == "main"
        assert result["price_range"] == "$$"
        assert result["image_url"] == "https://example.com/pad-thai.jpg"
        assert result["number"] is None

    def test_to_dict_with_none_values(self) -> None:
        """None値を含むto_dictメソッドのテスト"""
        dish = Dish(
            original_name="Simple",
            japanese_name="シンプル",
            description="シンプルな料理",
            spiciness=1,
            sweetness=1,
        )

        result = dish.to_dict()

        assert result["price_range"] is None
        assert result["image_url"] is None
        assert result["ingredients"] == []
        assert result["allergens"] == []
        assert result["category"] == "other"

    def test_from_dict(self) -> None:
        """from_dictメソッドのテスト"""
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

    def test_from_dict_with_missing_optional_fields(self) -> None:
        """オプショナルフィールドが欠けている場合のfrom_dictメソッドのテスト"""
        data = {
            "original_name": "Simple",
            "japanese_name": "シンプル",
            "description": "シンプルな料理",
            "spiciness": 1,
            "sweetness": 1,
        }

        dish = Dish.from_dict(data)

        assert dish.original_name == "Simple"
        assert dish.japanese_name == "シンプル"
        assert dish.ingredients == []
        assert dish.allergens == []
        assert dish.category == Category.OTHER
        assert dish.price_range is None
        assert dish.image_url is None

    def test_from_dict_with_invalid_category(self) -> None:
        """無効なカテゴリの場合、Category.OTHERにフォールバック"""
        data = {
            "original_name": "Test Dish",
            "japanese_name": "テスト料理",
            "description": "無効なカテゴリのテスト",
            "spiciness": 3,
            "sweetness": 3,
            "category": "invalid_category",  # 無効な値
        }

        dish = Dish.from_dict(data)

        assert dish.category == Category.OTHER

    def test_from_dict_with_invalid_price_range(self) -> None:
        """無効な価格帯の場合、Noneにフォールバック"""
        data = {
            "original_name": "Test Dish",
            "japanese_name": "テスト料理",
            "description": "無効な価格帯のテスト",
            "spiciness": 3,
            "sweetness": 3,
            "price_range": "$$$$$",  # 無効な値
        }

        dish = Dish.from_dict(data)

        assert dish.price_range is None

    def test_roundtrip_to_dict_from_dict(self) -> None:
        """to_dictとfrom_dictのラウンドトリップテスト"""
        original_dish = Dish(
            original_name="Tom Yum Goong",
            japanese_name="トムヤムクン",
            description="辛酸っぱいタイのスープ",
            spiciness=4,
            sweetness=2,
            ingredients=["エビ", "レモングラス", "唐辛子"],
            allergens=["甲殻類"],
            category=Category.MAIN,
            price_range=PriceRange.MODERATE,
            image_url="https://example.com/tom-yum.jpg",
        )

        # to_dict -> from_dict
        data = original_dish.to_dict()
        restored_dish = Dish.from_dict(data)

        # すべてのフィールドが一致することを確認
        assert restored_dish.original_name == original_dish.original_name
        assert restored_dish.japanese_name == original_dish.japanese_name
        assert restored_dish.description == original_dish.description
        assert restored_dish.spiciness == original_dish.spiciness
        assert restored_dish.sweetness == original_dish.sweetness
        assert restored_dish.ingredients == original_dish.ingredients
        assert restored_dish.allergens == original_dish.allergens
        assert restored_dish.category == original_dish.category
        assert restored_dish.price_range == original_dish.price_range
        assert restored_dish.image_url == original_dish.image_url
        assert restored_dish.number == original_dish.number
