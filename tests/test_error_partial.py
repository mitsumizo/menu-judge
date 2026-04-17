"""error.html パーシャルテンプレートのテスト"""

from collections.abc import Generator

import pytest
from flask import Flask, render_template_string


@pytest.fixture
def app() -> Generator[Flask, None, None]:
    """テスト用のFlaskアプリケーション"""
    app = Flask(
        __name__,
        template_folder="../app/templates",
    )
    return app  # type: ignore[return-value]


def test_error_partial_renders_with_default_title(app: Flask) -> None:
    """デフォルトタイトルでレンダリングされることを確認"""
    with app.app_context():
        template = """
        {% include 'partials/error.html' %}
        """
        html = render_template_string(template, message="テストエラーメッセージ")

        # デフォルトタイトルが表示される
        assert "エラーが発生しました" in html
        # メッセージが表示される
        assert "テストエラーメッセージ" in html


def test_error_partial_renders_with_custom_title(app: Flask) -> None:
    """カスタムタイトルでレンダリングされることを確認"""
    with app.app_context():
        template = """
        {% include 'partials/error.html' %}
        """
        html = render_template_string(
            template,
            title="ファイルがありません",
            message="画像ファイルを選択してください",
        )

        # カスタムタイトルが表示される
        assert "ファイルがありません" in html
        # メッセージが表示される
        assert "画像ファイルを選択してください" in html


def test_error_partial_renders_error_code(app: Flask) -> None:
    """エラーコードが表示されることを確認"""
    with app.app_context():
        template = """
        {% include 'partials/error.html' %}
        """
        html = render_template_string(
            template,
            title="解析に失敗しました",
            message="しばらく待ってから再度お試しください",
            code="API_ERROR",
        )

        # エラーコードが表示される
        assert "エラーコード: API_ERROR" in html


def test_error_partial_without_error_code(app: Flask) -> None:
    """エラーコードがない場合は表示されないことを確認"""
    with app.app_context():
        template = """
        {% include 'partials/error.html' %}
        """
        html = render_template_string(
            template,
            title="エラー",
            message="エラーが発生しました",
        )

        # エラーコードが表示されない
        assert "エラーコード:" not in html


def test_error_partial_has_close_button(app: Flask) -> None:
    """閉じるボタンが存在することを確認"""
    with app.app_context():
        template = """
        {% include 'partials/error.html' %}
        """
        html = render_template_string(template, message="テストエラー")

        # 閉じるボタンが存在する
        assert "閉じる" in html
        assert "onclick" in html
        assert "error-message" in html


def test_error_partial_has_error_icon(app: Flask) -> None:
    """エラーアイコンが表示されることを確認"""
    with app.app_context():
        template = """
        {% include 'partials/error.html' %}
        """
        html = render_template_string(template, message="テストエラー")

        # エラーアイコンが表示される
        assert "⚠️" in html


def test_error_partial_has_correct_css_classes(app: Flask) -> None:
    """正しいCSSクラスが適用されていることを確認"""
    with app.app_context():
        template = """
        {% include 'partials/error.html' %}
        """
        html = render_template_string(template, message="テストエラー")

        # 主要なCSSクラスが含まれる
        assert "id=\"error-message\"" in html
        assert "bg-red-500/10" in html
        assert "border-red-500/30" in html
        assert "rounded-lg" in html
        assert "animate-shake" in html
        assert "text-red-400" in html
        assert "text-red-500" in html


def test_error_partial_renders_all_error_types(app: Flask) -> None:
    """様々なエラータイプが正しくレンダリングされることを確認"""
    error_types = [
        {
            "title": "ファイルがありません",
            "message": "画像ファイルを選択してください",
            "code": "NO_FILE",
        },
        {
            "title": "非対応の形式です",
            "message": "JPEG, PNG, WebP形式の画像を使用してください",
            "code": "INVALID_FORMAT",
        },
        {
            "title": "ファイルが大きすぎます",
            "message": "10MB以下の画像を使用してください",
            "code": "FILE_TOO_LARGE",
        },
        {
            "title": "解析に失敗しました",
            "message": "しばらく待ってから再度お試しください",
            "code": "API_ERROR",
        },
        {
            "title": "料理が見つかりません",
            "message": "メニュー画像を使用してください",
            "code": "NO_DISHES",
        },
    ]

    with app.app_context():
        template = """
        {% include 'partials/error.html' %}
        """
        for error in error_types:
            html = render_template_string(template, **error)

            # 各要素が正しく表示される
            assert error["title"] in html
            assert error["message"] in html
            assert f"エラーコード: {error['code']}" in html
