"""Custom exceptions for web article extraction."""


class ExtractionError(Exception):
    """Base exception for article extraction errors."""


class ArticleDownloadError(ExtractionError):
    """Raised when article download fails."""


class ArticleParseError(ExtractionError):
    """Raised when article parsing fails."""


class InsufficientContentError(ExtractionError):
    """Raised when extracted content is insufficient."""


class HTMLFetchError(ExtractionError):
    """Raised when HTML content fetching fails."""


class LLMExtractionError(ExtractionError):
    """Raised when LLM extraction fails."""
