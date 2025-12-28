"""Factory class for AI providers."""

from __future__ import annotations

from .base import AIProvider, AIProviderError, APIKeyMissingError
from .claude_provider import ClaudeProvider


class UnknownProviderError(AIProviderError):
    """未知のプロバイダーが指定された."""

    pass


class AIProviderFactory:
    """AIプロバイダーを生成するファクトリークラス."""

    _providers: dict[str, type[AIProvider]] = {
        "claude": ClaudeProvider,
    }

    @classmethod
    def create(cls, api_key: str, provider_name: str = "claude") -> AIProvider:
        """
        AIプロバイダーを生成.

        Args:
            api_key: APIキー
            provider_name: プロバイダー名（デフォルト: claude）

        Returns:
            AIProvider: 生成されたプロバイダー

        Raises:
            UnknownProviderError: 未知のプロバイダーが指定された
            APIKeyMissingError: APIキーが空
        """
        if not api_key or not api_key.strip():
            raise APIKeyMissingError("API key is required")

        if provider_name not in cls._providers:
            raise UnknownProviderError(f"Unknown provider: {provider_name}")

        provider_class = cls._providers[provider_name]
        return provider_class(api_key)

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
        登録されているプロバイダー一覧.

        Returns:
            プロバイダー名のリスト
        """
        return list(cls._providers.keys())
