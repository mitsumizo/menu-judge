"""Factory class for AI providers."""

from __future__ import annotations

import os

from .base import AIProvider, AIProviderError, APIKeyMissingError
from .claude_provider import ClaudeProvider


class UnknownProviderError(AIProviderError):
    """未知のプロバイダーが指定された."""

    pass


class AIProviderFactory:
    """環境変数に基づいてプロバイダーを生成."""

    _providers: dict[str, type[AIProvider]] = {
        "claude": ClaudeProvider,
    }

    @classmethod
    def create(cls, provider_name: str | None = None) -> AIProvider:
        """
        AIプロバイダーを生成.

        Args:
            provider_name: プロバイダー名（Noneの場合は環境変数から取得）

        Returns:
            AIProvider: 生成されたプロバイダー

        Raises:
            UnknownProviderError: 未知のプロバイダーが指定された
            APIKeyMissingError: APIキーが設定されていない
        """
        name = provider_name or os.getenv("AI_PROVIDER", "claude")

        if name not in cls._providers:
            raise UnknownProviderError(f"Unknown provider: {name}")

        provider = cls._providers[name]()

        if not provider.is_available():
            raise APIKeyMissingError(f"API key not configured for {name}")

        return provider

    @classmethod
    def register(cls, name: str, provider_class: type[AIProvider]) -> None:
        """
        新しいプロバイダーを登録.

        Args:
            name: プロバイダー名
            provider_class: プロバイダークラス
        """
        cls._providers[name] = provider_class

    @classmethod
    def available_providers(cls) -> list[str]:
        """
        利用可能なプロバイダー一覧.

        Returns:
            利用可能なプロバイダー名のリスト
        """
        return [
            name
            for name, prov_cls in cls._providers.items()
            if prov_cls().is_available()
        ]
