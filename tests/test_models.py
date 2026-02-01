"""Tests for models module."""

from web_article_extractor.models import ExtractionResult


class TestModels:
    """Tests for data models."""

    def test_extraction_result_success(self):
        """Test ExtractionResult with successful extraction."""
        result = ExtractionResult(
            id_value="123",
            url="https://example.com",
            extracted_text="Sample article text",
            publication_date="2024-01-15",
            extraction_method="newspaper",
            status="success",
        )

        assert result.id_value == "123"
        assert result.url == "https://example.com"
        assert result.extracted_text == "Sample article text"
        assert result.publication_date == "2024-01-15"
        assert result.extraction_method == "newspaper"
        assert result.status == "success"
        assert result.error_message is None

    def test_extraction_result_error(self):
        """Test ExtractionResult with error."""
        result = ExtractionResult.create_error(
            id_value="456",
            url="https://example.com/error",
            error_message="All extraction methods failed",
        )

        assert result.id_value == "456"
        assert result.status == "error"
        assert result.error_message == "All extraction methods failed"
        assert result.publication_date is None
        assert result.extracted_text == ""

    def test_extraction_result_no_date(self):
        """Test ExtractionResult without publication date."""
        result = ExtractionResult(
            id_value="789",
            url="https://example.com/nodate",
            extracted_text="Article without date",
            publication_date=None,
            extraction_method="trafilatura",
            status="success",
        )

        assert result.publication_date is None
        assert result.status == "success"

    def test_extraction_result_gemini_method(self):
        """Test ExtractionResult with Gemini extraction."""
        result = ExtractionResult(
            id_value="999",
            url="https://example.com/gemini",
            extracted_text="Article extracted by Gemini",
            publication_date="2024-02-01",
            extraction_method="gemini",
            status="success",
        )

        assert result.extraction_method == "gemini"
        assert result.status == "success"

    def test_extraction_result_create_error_factory(self):
        """Test ExtractionResult.create_error factory method."""
        result = ExtractionResult.create_error(
            id_value="error-id",
            url="https://example.com/error",
            error_message="Test error message",
        )

        assert result.id_value == "error-id"
        assert result.url == "https://example.com/error"
        assert result.extracted_text == ""
        assert result.publication_date is None
        assert result.extraction_method == "none"
        assert result.status == "error"
        assert result.error_message == "Test error message"
