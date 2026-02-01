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

    @classmethod
    def create_error(cls, id_value: str, url: str, error_message: str) -> "ExtractionResult":
        """Create an error result."""
        return cls(
            id_value=id_value,
            url=url,
            extracted_text="",
            publication_date=None,
            extraction_method="none",
            status="error",
            error_message=error_message,
        )
