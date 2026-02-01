"""Web Article Extractor - A generic module for extracting text and dates from web articles."""

__version__ = "0.1.0"
__author__ = "Biagio Frusteri"
__license__ = "MIT"

from .exceptions import (
    ArticleDownloadError,
    ArticleParseError,
    ExtractionError,
    HTMLFetchError,
    InsufficientContentError,
    LLMExtractionError,
)
from .extractor import ArticleExtractor

__all__ = [
    "ArticleExtractor",
    "ExtractionError",
    "ArticleDownloadError",
    "ArticleParseError",
    "InsufficientContentError",
    "HTMLFetchError",
    "LLMExtractionError",
]
