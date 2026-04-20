"""Tests for app.translations.loader — TranslationLoader class."""

import pytest

from app.translations.loader import TranslationLoader


@pytest.fixture(autouse=True)
def clear_translation_cache():
    """Ensure TranslationLoader cache is clean before each test."""
    TranslationLoader.clear_cache()
    yield
    TranslationLoader.clear_cache()


class TestLoad:
    def test_load_english(self):
        translations = TranslationLoader.load("en")
        assert isinstance(translations, dict)
        assert len(translations) > 0

    def test_load_japanese(self):
        translations = TranslationLoader.load("ja")
        assert isinstance(translations, dict)
        assert len(translations) > 0

    def test_load_caches_result(self):
        first = TranslationLoader.load("en")
        second = TranslationLoader.load("en")
        assert first is second

    def test_unsupported_language_raises_value_error(self):
        with pytest.raises(ValueError, match="Unsupported language"):
            TranslationLoader.load("fr")


class TestGet:
    def test_get_with_valid_key(self):
        value = TranslationLoader.get("en", "ui.hero_title", "fallback")
        assert value != "fallback"
        assert isinstance(value, str)

    def test_get_with_missing_key_returns_fallback(self):
        value = TranslationLoader.get("en", "nonexistent.key", "my-fallback")
        assert value == "my-fallback"

    def test_get_with_missing_key_and_empty_fallback_returns_key(self):
        value = TranslationLoader.get("en", "nonexistent.key", "")
        assert value == "nonexistent.key"

    def test_get_with_unsupported_language_returns_fallback(self):
        value = TranslationLoader.get("zz", "ui.hero_title", "fallback")
        assert value == "fallback"

    def test_get_with_unsupported_language_no_fallback_returns_key(self):
        value = TranslationLoader.get("zz", "ui.hero_title", "")
        assert value == "ui.hero_title"

    def test_get_partial_path_not_dict_returns_fallback(self):
        value = TranslationLoader.get("en", "ui.hero_title.too.deep", "fallback")
        assert value == "fallback"


class TestClearCache:
    def test_clear_cache_removes_cached_entries(self):
        TranslationLoader.load("en")
        assert "en" in TranslationLoader._cache
        TranslationLoader.clear_cache()
        assert "en" not in TranslationLoader._cache


class TestGetSupportedLanguages:
    def test_returns_list_with_en_and_ja(self):
        langs = TranslationLoader.get_supported_languages()
        assert "en" in langs
        assert "ja" in langs

    def test_returns_copy_not_internal_list(self):
        langs = TranslationLoader.get_supported_languages()
        langs.append("fr")
        assert "fr" not in TranslationLoader.get_supported_languages()
