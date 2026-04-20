"""error.html パーシャルテンプレートのテスト"""

import pytest
from flask import Flask, render_template_string

from app import create_app

JA_PATH = "/?lang=ja"


@pytest.fixture
def app() -> Flask:
    """テスト用のFlaskアプリケーション（t()などのJinja2グローバルを含む）"""
    return create_app({"TESTING": True, "SECRET_KEY": "test-secret-key"})


def test_error_partial_renders_with_default_title(app: Flask) -> None:
    """デフォルトタイトルでレンダリングされることを確認"""
    with app.test_request_context(JA_PATH):
        template = """
        {% include 'partials/error.html' %}
        """
        html = render_template_string(template, message="テストエラーメッセージ")

        assert "エラーが発生しました" in html
        assert "テストエラーメッセージ" in html


def test_error_partial_renders_with_custom_title(app: Flask) -> None:
    """カスタムタイトルでレンダリングされることを確認"""
    with app.test_request_context(JA_PATH):
        template = """
        {% include 'partials/error.html' %}
        """
        html = render_template_string(
            template,
            title="ファイルがありません",
            message="画像ファイルを選択してください",
        )

        assert "ファイルがありません" in html
        assert "画像ファイルを選択してください" in html


def test_error_partial_renders_error_code(app: Flask) -> None:
    """エラーコードが表示されることを確認"""
    with app.test_request_context(JA_PATH):
        template = """
        {% include 'partials/error.html' %}
        """
        html = render_template_string(
            template,
            title="解析に失敗しました",
            message="しばらく待ってから再度お試しください",
            code="API_ERROR",
        )

        assert "エラーコード: API_ERROR" in html


def test_error_partial_without_error_code(app: Flask) -> None:
    """エラーコードがない場合は表示されないことを確認"""
    with app.test_request_context(JA_PATH):
        template = """
        {% include 'partials/error.html' %}
        """
        html = render_template_string(
            template,
            title="エラー",
            message="エラーが発生しました",
        )

        assert "エラーコード:" not in html


def test_error_partial_has_close_button(app: Flask) -> None:
    """閉じるボタンが存在することを確認"""
    with app.test_request_context(JA_PATH):
        template = """
        {% include 'partials/error.html' %}
        """
        html = render_template_string(template, message="テストエラー")

        assert "閉じる" in html
        assert "onclick" in html
        assert "error-message" in html


def test_error_partial_has_error_icon(app: Flask) -> None:
    """エラーアイコンが表示されることを確認（SVG形式）"""
    with app.test_request_context(JA_PATH):
        template = """
        {% include 'partials/error.html' %}
        """
        html = render_template_string(template, message="テストエラー")

        # SVGエラーアイコンが表示される
        assert "<svg" in html
        assert 'role="alert"' in html


def test_error_partial_has_correct_css_classes(app: Flask) -> None:
    """正しいCSSクラスが適用されていることを確認"""
    with app.test_request_context(JA_PATH):
        template = """
        {% include 'partials/error.html' %}
        """
        html = render_template_string(template, message="テストエラー")

        assert 'id="error-message"' in html
        assert "bg-red-50" in html
        assert "border-red-200" in html
        assert "rounded-xl" in html
        assert "animate-shake" in html
        assert "text-red-700" in html


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

    with app.test_request_context(JA_PATH):
        template = """
        {% include 'partials/error.html' %}
        """
        for error in error_types:
            html = render_template_string(template, **error)

            assert error["title"] in html
            assert error["message"] in html
            assert f"エラーコード: {error['code']}" in html
