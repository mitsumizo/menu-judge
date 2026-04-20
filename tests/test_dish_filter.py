"""カテゴリフィルタ機能のテスト（Issue #48）

Alpine.js によるクライアント側フィルタリングの構造を検証する。
ブラウザ上の実動作（クリックで表示が切り替わる等）は別途 E2E で確認する。
"""

from __future__ import annotations

import pytest
from flask import Flask, render_template

from app import create_app
from app.models.dish import Category, Dish


@pytest.fixture
def app() -> Flask:
    """テスト用の Flask アプリケーション"""
    return create_app({"TESTING": True, "SECRET_KEY": "test-secret-key"})


@pytest.fixture
def multi_category_dishes() -> list[Dish]:
    """複数カテゴリをまたぐ料理リスト"""
    return [
        Dish(
            original_name="Spring Roll",
            translated_name="春巻き",
            description="前菜",
            spiciness=1,
            sweetness=1,
            category=Category.APPETIZER,
            number=1,
        ),
        Dish(
            original_name="Pad Thai",
            translated_name="パッタイ",
            description="メイン",
            spiciness=2,
            sweetness=3,
            category=Category.MAIN,
            number=2,
        ),
        Dish(
            original_name="Green Curry",
            translated_name="グリーンカレー",
            description="メイン",
            spiciness=4,
            sweetness=2,
            category=Category.MAIN,
            number=3,
        ),
        Dish(
            original_name="Mango Sticky Rice",
            translated_name="マンゴーもち米",
            description="デザート",
            spiciness=1,
            sweetness=5,
            category=Category.DESSERT,
            number=4,
        ),
    ]


def _render(app: Flask, dishes: list[Dish]) -> str:
    with app.test_request_context("/?lang=ja"):
        return render_template(
            "partials/dish_list.html",
            dishes=dishes,
            provider="claude",
            processing_time=0.1,
        )


def test_filter_container_is_rendered(app: Flask, multi_category_dishes: list[Dish]) -> None:
    """カテゴリフィルタのコンテナがレンダリングされる"""
    html = _render(app, multi_category_dishes)
    assert 'data-testid="category-filter"' in html


def test_filter_uses_alpine_state(app: Flask, multi_category_dishes: list[Dish]) -> None:
    """Alpine.js の selectedCategory 状態が 'all' 初期化で存在する"""
    html = _render(app, multi_category_dishes)
    # 親スコープの x-data に selectedCategory: 'all' を持つ
    assert "selectedCategory" in html
    assert "'all'" in html


def test_filter_renders_all_button(app: Flask, multi_category_dishes: list[Dish]) -> None:
    """『すべて表示』ボタンがレンダリングされる"""
    html = _render(app, multi_category_dishes)
    # data 属性で識別可能
    assert 'data-category="all"' in html
    # ja 翻訳の文言
    assert "すべて" in html


def test_filter_renders_button_per_present_category(
    app: Flask, multi_category_dishes: list[Dish]
) -> None:
    """解析結果に存在するカテゴリごとにフィルタボタンが出る"""
    html = _render(app, multi_category_dishes)
    # dishes に含まれるカテゴリ: appetizer, main, dessert
    assert 'data-category="appetizer"' in html
    assert 'data-category="main"' in html
    assert 'data-category="dessert"' in html
    # 含まれないものは描画しない（ノイズ抑制）
    assert 'data-category="beverage"' not in html


def test_filter_buttons_set_selected_category_on_click(
    app: Flask, multi_category_dishes: list[Dish]
) -> None:
    """各ボタンの @click で selectedCategory を更新する"""
    html = _render(app, multi_category_dishes)
    assert "selectedCategory = 'all'" in html
    assert "selectedCategory = 'main'" in html


def test_filter_button_highlights_active_state(
    app: Flask, multi_category_dishes: list[Dish]
) -> None:
    """選択中のボタンは :class バインドでアクティブ表示される"""
    html = _render(app, multi_category_dishes)
    # アクティブ判定に selectedCategory === '<cat>' を使う
    assert "selectedCategory === 'all'" in html
    assert "selectedCategory === 'main'" in html


def test_filter_button_shows_category_count(
    app: Flask, multi_category_dishes: list[Dish]
) -> None:
    """各ボタンに件数が表示される（main は 2 件、dessert は 1 件）"""
    html = _render(app, multi_category_dishes)
    # data-count 属性として件数を保持
    assert 'data-count="2"' in html  # main
    assert 'data-count="1"' in html  # appetizer/dessert
    # 全件数（4）も all ボタン側で出す
    assert 'data-count="4"' in html


def test_dish_cards_have_category_data_attribute(
    app: Flask, multi_category_dishes: list[Dish]
) -> None:
    """各 dish-card が自身のカテゴリを data 属性で持つ（Alpine フィルタの鍵）"""
    html = _render(app, multi_category_dishes)
    assert 'data-category="main"' in html
    assert 'data-category="appetizer"' in html
    assert 'data-category="dessert"' in html


def test_dish_cards_use_x_show_for_filtering(
    app: Flask, multi_category_dishes: list[Dish]
) -> None:
    """料理カードは x-show で selectedCategory との一致を見て表示を切替える"""
    html = _render(app, multi_category_dishes)
    # x-show 内で selectedCategory と card のカテゴリを比較する式が入る
    assert "selectedCategory === 'all'" in html
    # 各カテゴリの条件が x-show 上に並ぶ
    assert "x-show=\"selectedCategory === 'all' || selectedCategory === 'main'\"" in html


def test_filtered_count_uses_alpine_x_text(
    app: Flask, multi_category_dishes: list[Dish]
) -> None:
    """フィルタ後の件数は Alpine の x-text で動的に出す"""
    html = _render(app, multi_category_dishes)
    assert 'data-testid="filtered-count"' in html
    # x-text で件数を差し替え（実装で使う変数名は filteredCount を推奨）
    assert "filteredCount" in html


def test_filter_is_hidden_when_no_dishes(app: Flask) -> None:
    """料理が 0 件のときはフィルタを出さない"""
    html = _render(app, [])
    assert 'data-testid="category-filter"' not in html


def test_filter_is_hidden_when_only_one_category(app: Flask) -> None:
    """単一カテゴリしかない場合、フィルタUIは不要なので描画しない"""
    dishes = [
        Dish(
            original_name=f"Dish{i}",
            translated_name=f"料理{i}",
            description="desc",
            spiciness=1,
            sweetness=1,
            category=Category.MAIN,
            number=i,
        )
        for i in range(1, 4)
    ]
    html = _render(app, dishes)
    assert 'data-testid="category-filter"' not in html
