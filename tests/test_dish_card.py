"""dish_card.html コンポーネントのテスト"""

from typing import Generator

import pytest
from flask import Flask, render_template_string

from app.models.dish import Category, Dish, PriceRange


@pytest.fixture
def app() -> Generator[Flask, None, None]:
    """テスト用のFlaskアプリケーション"""
    app = Flask(
        __name__,
        template_folder="../app/templates",
    )
    return app  # type: ignore[return-value]


@pytest.fixture
def sample_dish() -> Dish:
    """テスト用のサンプル料理データ"""
    return Dish(
        original_name="Pad Thai",
        japanese_name="パッタイ",
        description="米麺を使ったタイ風焼きそば",
        spiciness=2,
        sweetness=3,
        ingredients=["米麺", "エビ", "卵", "もやし", "ピーナッツ"],
        allergens=["甲殻類", "卵", "ナッツ"],
        category=Category.MAIN,
        price_range=PriceRange.MODERATE,
    )


def test_dish_card_renders_basic_info(app: Flask, sample_dish: Dish) -> None:
    """料理カードが基本情報を表示することを確認"""
    with app.app_context():
        template = """
        {% from 'components/dish_card.html' import dish_card %}
        {{ dish_card(dish) }}
        """
        html = render_template_string(template, dish=sample_dish)

        # 料理名が表示される
        assert "パッタイ" in html
        assert "Pad Thai" in html

        # 説明が表示される
        assert "米麺を使ったタイ風焼きそば" in html


def test_dish_card_renders_price_range(app: Flask, sample_dish: Dish) -> None:
    """価格帯が表示されることを確認"""
    with app.app_context():
        template = """
        {% from 'components/dish_card.html' import dish_card %}
        {{ dish_card(dish) }}
        """
        html = render_template_string(template, dish=sample_dish)

        # 価格帯が表示される
        assert "$$" in html


def test_dish_card_renders_without_price_range(app: Flask, sample_dish: Dish) -> None:
    """価格帯がない場合でもレンダリングできることを確認"""
    sample_dish.price_range = None

    with app.app_context():
        template = """
        {% from 'components/dish_card.html' import dish_card %}
        {{ dish_card(dish) }}
        """
        html = render_template_string(template, dish=sample_dish)

        # 基本情報は表示される
        assert "パッタイ" in html


def test_dish_card_renders_spiciness_indicator(app: Flask, sample_dish: Dish) -> None:
    """辛さインジケーターが表示されることを確認"""
    with app.app_context():
        template = """
        {% from 'components/dish_card.html' import dish_card %}
        {{ dish_card(dish) }}
        """
        html = render_template_string(template, dish=sample_dish)

        # 辛さの絵文字が表示される
        assert "🌶️" in html

        # 辛さレベル2なので、bg-red-500が2つ、bg-slate-600が3つ
        assert html.count("bg-red-500") >= 2
        assert html.count("bg-slate-600") >= 3


def test_dish_card_renders_sweetness_indicator(app: Flask, sample_dish: Dish) -> None:
    """甘さインジケーターが表示されることを確認"""
    with app.app_context():
        template = """
        {% from 'components/dish_card.html' import dish_card %}
        {{ dish_card(dish) }}
        """
        html = render_template_string(template, dish=sample_dish)

        # 甘さの絵文字が表示される
        assert "🍯" in html

        # 甘さレベル3なので、bg-amber-500が3つ
        assert html.count("bg-amber-500") >= 3


def test_dish_card_renders_ingredients(app: Flask, sample_dish: Dish) -> None:
    """材料タグが表示されることを確認"""
    with app.app_context():
        template = """
        {% from 'components/dish_card.html' import dish_card %}
        {{ dish_card(dish) }}
        """
        html = render_template_string(template, dish=sample_dish)

        # 各材料が表示される
        for ingredient in sample_dish.ingredients:
            assert ingredient in html


def test_dish_card_renders_allergens(app: Flask, sample_dish: Dish) -> None:
    """アレルギー情報が表示されることを確認"""
    with app.app_context():
        template = """
        {% from 'components/dish_card.html' import dish_card %}
        {{ dish_card(dish) }}
        """
        html = render_template_string(template, dish=sample_dish)

        # アレルギー警告が表示される
        assert "⚠️ アレルギー:" in html
        assert "甲殻類" in html
        assert "卵" in html
        assert "ナッツ" in html


def test_dish_card_renders_without_allergens(app: Flask, sample_dish: Dish) -> None:
    """アレルギー情報がない場合、警告が表示されないことを確認"""
    sample_dish.allergens = []

    with app.app_context():
        template = """
        {% from 'components/dish_card.html' import dish_card %}
        {{ dish_card(dish) }}
        """
        html = render_template_string(template, dish=sample_dish)

        # アレルギー警告が表示されない
        assert "⚠️ アレルギー:" not in html


def test_dish_card_renders_category(app: Flask, sample_dish: Dish) -> None:
    """カテゴリバッジが表示されることを確認"""
    with app.app_context():
        template = """
        {% from 'components/dish_card.html' import dish_card %}
        {{ dish_card(dish) }}
        """
        html = render_template_string(template, dish=sample_dish)

        # カテゴリが表示される
        assert "main" in html


def test_dish_card_has_correct_css_classes(app: Flask, sample_dish: Dish) -> None:
    """正しいCSSクラスが適用されていることを確認"""
    with app.app_context():
        template = """
        {% from 'components/dish_card.html' import dish_card %}
        {{ dish_card(dish) }}
        """
        html = render_template_string(template, dish=sample_dish)

        # 主要なCSSクラスが含まれる
        assert "dish-card" in html
        assert "bg-surface" in html
        assert "rounded-xl" in html
        assert "shadow-lg" in html
        assert "hover:shadow-xl" in html
        assert "transition-all" in html
        assert "border-slate-700" in html
        assert "hover:border-primary" in html
