"""Cover TranslationLoader.load FileNotFoundError branch (line 47)."""

import pytest

from app.translations.loader import TranslationLoader


class TestMissingTranslationFile:
    def test_load_raises_when_file_missing(self, monkeypatch):
        """Add a fake supported language whose JSON file does not exist."""
        TranslationLoader.clear_cache()
        monkeypatch.setattr(
            TranslationLoader, "_supported_languages", ["en", "ja", "xx"]
        )
        with pytest.raises(FileNotFoundError, match="Translation file not found"):
            TranslationLoader.load("xx")

    def test_get_returns_fallback_when_file_missing(self, monkeypatch):
        """TranslationLoader.get should swallow FileNotFoundError and return fallback."""
        TranslationLoader.clear_cache()
        monkeypatch.setattr(
            TranslationLoader, "_supported_languages", ["en", "ja", "xx"]
        )
        result = TranslationLoader.get("xx", "some.key", "FALLBACK")
        assert result == "FALLBACK"
