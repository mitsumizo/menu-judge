"""Base class for AI providers using Strategy Pattern."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.models.dish import Dish


@dataclass
class AnalysisResult:
    """
    Menu analysis result.

    Attributes:
        dishes: List of analyzed dishes
        raw_response: Raw API response
        provider: Provider name
        processing_time: Processing time in seconds
    """

    dishes: list[Dish]
    raw_response: str
    provider: str
    processing_time: float


class AIProvider(ABC):
    """Base class for AI providers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Get provider name.

        Returns:
            Provider name
        """
        pass

    @abstractmethod
    def analyze_menu(self, image_data: bytes, mime_type: str) -> AnalysisResult:
        """
        Analyze menu image and return dish information.

        Args:
            image_data: Image binary data
            mime_type: Image MIME type (image/jpeg, image/png, etc.)

        Returns:
            AnalysisResult: Analysis result

        Raises:
            AIProviderError: API call error
        """
        pass

    @classmethod
    @abstractmethod
    def is_available(cls) -> bool:
        """
        Check if provider is available.

        Returns:
            True if provider is available, False otherwise
        """
        pass


class AIProviderError(Exception):
    """Base class for AI provider errors."""

    pass


class APIKeyMissingError(AIProviderError):
    """API key is not configured."""

    pass


class APICallError(AIProviderError):
    """API call failed."""

    pass
