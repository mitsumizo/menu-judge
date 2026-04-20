"""Edge-case tests for app.models.dish — uncovered validation branches."""

import pytest

from app.models.dish import BoundingBox, Dish


class TestBoundingBoxTypeCheck:
    def test_non_numeric_x_raises_type_error(self):
        with pytest.raises(TypeError, match="x must be a number"):
            BoundingBox(x="0.1", y=0.1, width=0.1, height=0.1)

    def test_non_numeric_width_raises_type_error(self):
        with pytest.raises(TypeError, match="width must be a number"):
            BoundingBox(x=0.1, y=0.1, width=None, height=0.1)


class TestDishFromDictInvalidBoundingBox:
    def _base_dish_dict(self) -> dict:
        return {
            "original_name": "Pad Thai",
            "translated_name": "パッタイ",
            "description": "タイ風焼きそば",
            "spiciness": 2,
            "sweetness": 3,
        }

    def test_invalid_bounding_box_falls_back_to_none(self):
        data = self._base_dish_dict()
        data["bounding_box"] = {"x": 0.1}  # missing required fields
        dish = Dish.from_dict(data)
        assert dish.bounding_box is None

    def test_bounding_box_with_out_of_range_values_falls_back_to_none(self):
        data = self._base_dish_dict()
        data["bounding_box"] = {"x": 2.0, "y": 0.1, "width": 0.1, "height": 0.1}
        dish = Dish.from_dict(data)
        assert dish.bounding_box is None
