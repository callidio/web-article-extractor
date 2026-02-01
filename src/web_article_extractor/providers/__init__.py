"""API Provider implementations for web article extraction."""

from .base import BaseAPIProvider
from .gemini import GeminiAPI

__all__ = ["BaseAPIProvider", "GeminiAPI"]
