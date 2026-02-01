"""Data models for web article extractor."""

from dataclasses import dataclass


@dataclass
class ExtractionResult:
    """Result of article extraction."""

    id_value: str
    url: str
    extracted_text: str
    publication_date: str | None
    extraction_method: str
    status: str
    error_message: str | None = None
