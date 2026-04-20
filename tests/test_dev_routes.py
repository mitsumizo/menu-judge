"""Tests for app.routes.dev — development blueprint routes."""

import pytest

from app import create_app
from app.models.dish import Category, Dish
from app.routes.dev import get_mock_dishes


@pytest.fixture
def debug_client():
    """Test client with the dev blueprint registered (DEBUG=True)."""
    app = create_app(
        {
            "TESTING": True,
            "DEBUG": True,
            "SECRET_KEY": "test-secret-key",
        }
    )
    return app.test_client()


class TestGetMockDishes:
    def test_returns_ten_dishes(self):
        dishes = get_mock_dishes()
        assert isinstance(dishes, list)
        assert len(dishes) == 10
        assert all(isinstance(d, Dish) for d in dishes)

    def test_each_dish_has_valid_fields(self):
        for dish in get_mock_dishes():
            assert dish.original_name
            assert dish.translated_name
            assert dish.description
            assert 1 <= dish.spiciness <= 5
            assert 1 <= dish.sweetness <= 5
            assert isinstance(dish.ingredients, list)
            assert isinstance(dish.allergens, list)
            assert isinstance(dish.category, Category)
            assert dish.bounding_box is not None

    def test_contains_multiple_categories(self):
        categories = {d.category for d in get_mock_dishes()}
        assert Category.APPETIZER in categories
        assert Category.MAIN in categories
        assert Category.DESSERT in categories
        assert Category.BEVERAGE in categories


class TestMockResultsRoute:
    def test_returns_200(self, debug_client):
        response = debug_client.get("/dev/mock-results")
        assert response.status_code == 200

    def test_renders_dish_fragment(self, debug_client):
        response = debug_client.get("/dev/mock-results")
        body = response.data.decode("utf-8")
        assert "Kottu" in body or "Pad" in body or "Curry" in body


class TestMockPageRoute:
    def test_returns_200(self, debug_client):
        response = debug_client.get("/dev/mock-page")
        assert response.status_code == 200

    def test_is_full_html_page(self, debug_client):
        response = debug_client.get("/dev/mock-page")
        body = response.data.decode("utf-8")
        assert "<html" in body.lower() or "<!doctype" in body.lower()


class TestDevBlueprintNotRegisteredInProduction:
    def test_mock_routes_return_404_without_debug(self):
        app = create_app({"TESTING": True, "DEBUG": False, "SECRET_KEY": "test-secret-key"})
        client = app.test_client()
        assert client.get("/dev/mock-results").status_code == 404
        assert client.get("/dev/mock-page").status_code == 404
