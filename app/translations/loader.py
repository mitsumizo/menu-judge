"""Translation loader for Menu Judge application."""

import json
from pathlib import Path
from typing import Any


class TranslationLoader:
    """翻訳ファイルを読み込むクラス

    このクラスは指定された言語の翻訳JSONファイルを読み込み、
    キャッシュして効率的に翻訳データを提供します。
    """

    _cache: dict[str, dict[str, Any]] = {}
    _supported_languages = ["en", "ja"]

    @classmethod
    def load(cls, language: str) -> dict[str, Any]:
        """翻訳を読み込む

        Args:
            language: 言語コード ('en' または 'ja')

        Returns:
            dict[str, Any]: 翻訳辞書

        Raises:
            ValueError: サポートされていない言語の場合
            FileNotFoundError: 翻訳ファイルが見つからない場合
        """
        if language not in cls._supported_languages:
            raise ValueError(
                f"Unsupported language: {language}. "
                f"Supported languages: {', '.join(cls._supported_languages)}"
            )

        # キャッシュチェック
        if language in cls._cache:
            return cls._cache[language]

        # 翻訳ファイルのパス
        translations_dir = Path(__file__).parent
        file_path = translations_dir / f"{language}.json"

        if not file_path.exists():
            raise FileNotFoundError(f"Translation file not found: {file_path}")

        # JSONファイルを読み込み
        with open(file_path, encoding="utf-8") as f:
            translations = json.load(f)

        # キャッシュに保存
        cls._cache[language] = translations

        return translations

    @classmethod
    def get(cls, language: str, key: str, fallback: str = "") -> str:
        """ドット記法で翻訳を取得

        Args:
            language: 言語コード
            key: ドット記法のキー (例: 'ui.hero_title')
            fallback: キーが見つからない場合のフォールバック

        Returns:
            str: 翻訳文字列

        Example:
            >>> TranslationLoader.get('en', 'ui.hero_title')
            'Decode Any Menu'
        """
        try:
            translations = cls.load(language)
            keys = key.split(".")
            value = translations

            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return fallback or key

            return str(value) if value is not None else fallback
        except (ValueError, FileNotFoundError):
            return fallback or key

    @classmethod
    def clear_cache(cls) -> None:
        """キャッシュをクリア（主にテスト用）"""
        cls._cache.clear()

    @classmethod
    def get_supported_languages(cls) -> list[str]:
        """サポートされている言語のリストを取得

        Returns:
            list[str]: サポートされている言語コードのリスト
        """
        return cls._supported_languages.copy()
