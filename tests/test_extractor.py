"""Tests for extractor module."""

from unittest.mock import Mock, patch

import pandas as pd
import pytest
import requests

from web_article_extractor.config import Config
from web_article_extractor.extractor import ArticleExtractor
from web_article_extractor.models import ExtractionResult


class TestArticleExtractor:  # pylint: disable=too-many-public-methods
    """Tests for ArticleExtractor class."""

    def test_normalize_date_valid(self):
        """Test date normalization with valid dates."""
        extractor = ArticleExtractor(gemini_api=Mock())

        assert extractor.normalize_date("2024-01-15") == "2024-01-15"
        assert extractor.normalize_date("January 15, 2024") == "2024-01-15"
        assert extractor.normalize_date("15/01/2024") == "2024-01-15"

    def test_normalize_date_invalid(self):
        """Test date normalization with invalid dates."""
        extractor = ArticleExtractor(gemini_api=Mock())

        assert extractor.normalize_date(None) is None
        assert extractor.normalize_date("") is None
        assert extractor.normalize_date("invalid date") is None

    def test_extract_from_url_empty_url(self):
        """Test extraction with empty URL."""
        extractor = ArticleExtractor(gemini_api=Mock())

        result = extractor.extract_from_url("", "test-id")
        assert result.status == "error"
        assert result.error_message == "Empty or invalid URL"

    def test_extract_from_url_none_url(self):
        """Test extraction with None URL."""
        extractor = ArticleExtractor(gemini_api=Mock())

        result = extractor.extract_from_url(None, "test-id")
        assert result.status == "error"
        assert result.error_message == "Empty or invalid URL"

    @patch("web_article_extractor.extractor.Article")
    def test_extract_with_newspaper_success(self, mock_article_class):
        """Test successful extraction with newspaper3k."""
        mock_article = Mock()
        mock_article.text = "Article text content " * 20  # Ensure > 100 chars
        mock_article.publish_date = None
        mock_article_class.return_value = mock_article

        extractor = ArticleExtractor(gemini_api=Mock())
        text, _ = extractor.extract_with_newspaper("https://example.com")

        assert text is not None
        assert len(text) > 100

    @patch("web_article_extractor.extractor.Article")
    def test_extract_with_newspaper_failure(self, mock_article_class):
        """Test failed extraction with newspaper3k."""
        mock_article = Mock()
        mock_article.download.side_effect = OSError("Download failed")
        mock_article_class.return_value = mock_article

        extractor = ArticleExtractor(gemini_api=Mock())
        text, date = extractor.extract_with_newspaper("https://example.com")

        assert text is None
        assert date is None

    @patch("web_article_extractor.extractor.Article")
    def test_extract_with_newspaper_short_text(self, mock_article_class):
        """Test extraction with insufficient text."""
        mock_article = Mock()
        mock_article.text = "Short"  # Less than 100 chars
        mock_article.publish_date = None
        mock_article_class.return_value = mock_article

        extractor = ArticleExtractor(gemini_api=Mock())
        text, date = extractor.extract_with_newspaper("https://example.com")

        assert text is None
        assert date is None

    @patch("web_article_extractor.extractor.trafilatura.fetch_url")
    @patch("web_article_extractor.extractor.trafilatura.extract")
    def test_extract_with_trafilatura_success(self, mock_extract, mock_fetch):
        """Test successful extraction with trafilatura."""
        mock_fetch.return_value = "<html>content</html>"
        mock_extract.return_value = "Article text content " * 20

        extractor = ArticleExtractor(gemini_api=Mock())
        text, _ = extractor.extract_with_trafilatura("https://example.com")

        assert text is not None
        assert len(text) > 100

    @patch("web_article_extractor.extractor.trafilatura.fetch_url")
    def test_extract_with_trafilatura_failure(self, mock_fetch):
        """Test failed extraction with trafilatura."""
        mock_fetch.return_value = None

        extractor = ArticleExtractor(gemini_api=Mock())
        text, date = extractor.extract_with_trafilatura("https://example.com")

        assert text is None
        assert date is None

    @patch("web_article_extractor.extractor.requests.get")
    def test_extract_with_gemini_success(self, mock_get):
        """Test successful extraction with Gemini."""
        mock_response = Mock()
        mock_response.text = "<html>content</html>"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        mock_gemini = Mock()
        mock_gemini.query.return_value = '{"text": "' + ("Article text " * 20) + '", "date": "2024-01-15"}'

        extractor = ArticleExtractor(gemini_api=mock_gemini)
        text, date = extractor.extract_with_gemini("https://example.com")

        assert text is not None
        assert len(text) > 100
        assert date == "2024-01-15"

    @patch("web_article_extractor.extractor.requests.get")
    def test_extract_with_gemini_failure(self, mock_get):
        """Test failed extraction with Gemini."""
        mock_get.side_effect = requests.RequestException("Request failed")

        mock_gemini = Mock()
        extractor = ArticleExtractor(gemini_api=mock_gemini)
        text, date = extractor.extract_with_gemini("https://example.com")

        assert text is None
        assert date is None

    @patch("web_article_extractor.extractor.ArticleExtractor.extract_with_newspaper")
    def test_extract_from_url_newspaper_success(self, mock_newspaper):
        """Test successful extraction using newspaper."""
        mock_newspaper.return_value = ("Article text " * 20, "2024-01-15")

        extractor = ArticleExtractor(gemini_api=Mock())
        result = extractor.extract_from_url("https://example.com", "test-id")

        assert result.status == "success"
        assert result.extraction_method == "newspaper"
        assert result.publication_date == "2024-01-15"

    @patch("web_article_extractor.extractor.ArticleExtractor.extract_with_newspaper")
    @patch("web_article_extractor.extractor.ArticleExtractor.extract_with_trafilatura")
    def test_extract_from_url_trafilatura_fallback(self, mock_trafilatura, mock_newspaper):
        """Test fallback to trafilatura when newspaper fails."""
        mock_newspaper.return_value = (None, None)
        mock_trafilatura.return_value = ("Article text " * 20, "2024-01-15")

        extractor = ArticleExtractor(gemini_api=Mock())
        result = extractor.extract_from_url("https://example.com", "test-id")

        assert result.status == "success"
        assert result.extraction_method == "trafilatura"

    @patch("web_article_extractor.extractor.ArticleExtractor.extract_with_newspaper")
    @patch("web_article_extractor.extractor.ArticleExtractor.extract_with_trafilatura")
    @patch("web_article_extractor.extractor.ArticleExtractor.extract_with_gemini")
    def test_extract_from_url_gemini_fallback(self, mock_gemini, mock_trafilatura, mock_newspaper):
        """Test fallback to Gemini when both parsers fail."""
        mock_newspaper.return_value = (None, None)
        mock_trafilatura.return_value = (None, None)
        mock_gemini.return_value = ("Article text " * 20, "2024-01-15")

        extractor = ArticleExtractor(gemini_api=Mock())
        result = extractor.extract_from_url("https://example.com", "test-id")

        assert result.status == "success"
        assert result.extraction_method == "gemini"

    @patch("web_article_extractor.extractor.ArticleExtractor.extract_with_newspaper")
    @patch("web_article_extractor.extractor.ArticleExtractor.extract_with_trafilatura")
    @patch("web_article_extractor.extractor.ArticleExtractor.extract_with_gemini")
    def test_extract_from_url_all_methods_fail(self, mock_gemini, mock_trafilatura, mock_newspaper):
        """Test when all extraction methods fail."""
        mock_newspaper.return_value = (None, None)
        mock_trafilatura.return_value = (None, None)
        mock_gemini.return_value = (None, None)

        extractor = ArticleExtractor(gemini_api=Mock())
        result = extractor.extract_from_url("https://example.com", "test-id")

        assert result.status == "error"
        assert result.error_message == "All extraction methods failed"

    def test_process_csv(self, tmp_path):
        """Test CSV processing."""
        # Create test CSV
        input_csv = tmp_path / "input.csv"
        input_data = pd.DataFrame(
            {
                "id": ["1", "2"],
                "url1": ["https://example.com/1", "https://example.com/2"],
                "url2": ["https://test.com/1", "https://test.com/2"],
            }
        )
        input_data.to_csv(input_csv, index=False)

        # Create config
        config = Config(id_column="id", url_columns=["url1", "url2"])

        # Mock extractor
        extractor = ArticleExtractor(gemini_api=Mock())

        with patch.object(extractor, "extract_from_url") as mock_extract:
            mock_extract.return_value = ExtractionResult(
                id_value="1",
                url="https://example.com/1",
                extracted_text="Test article",
                publication_date="2024-01-15",
                extraction_method="newspaper",
                status="success",
            )

            output_csv = tmp_path / "output.csv"
            extractor.process_csv(input_csv, output_csv, config)

            # Verify output
            assert output_csv.exists()
            output_data = pd.read_csv(output_csv)
            assert len(output_data) == 4  # 2 rows * 2 URL columns

    def test_process_csv_missing_id_column(self, tmp_path):
        """Test error when ID column is missing."""
        input_csv = tmp_path / "input.csv"
        input_data = pd.DataFrame({"url": ["https://example.com"]})
        input_data.to_csv(input_csv, index=False)

        config = Config(id_column="id", url_columns=["url"])
        extractor = ArticleExtractor(gemini_api=Mock())
        output_csv = tmp_path / "output.csv"

        with pytest.raises(ValueError, match="ID column 'id' not found"):
            extractor.process_csv(input_csv, output_csv, config)

    def test_process_csv_missing_url_column(self, tmp_path):
        """Test error when URL column is missing."""
        input_csv = tmp_path / "input.csv"
        input_data = pd.DataFrame({"id": ["1"]})
        input_data.to_csv(input_csv, index=False)

        config = Config(id_column="id", url_columns=["url"])
        extractor = ArticleExtractor(gemini_api=Mock())
        output_csv = tmp_path / "output.csv"

        with pytest.raises(ValueError, match="URL columns not found"):
            extractor.process_csv(input_csv, output_csv, config)

    def test_extract_date_from_url(self):
        """Test date extraction from URL patterns."""
        extractor = ArticleExtractor(gemini_api=Mock())

        # Test /2024/01/15/ pattern
        assert extractor.extract_date_from_url("https://example.com/2024/01/15/article") == "2024-01-15"
        # Test 2024-01-15 pattern
        assert extractor.extract_date_from_url("https://example.com/article-2024-01-15") == "2024-01-15"
        # Test no date
        assert extractor.extract_date_from_url("https://example.com/article") is None

    def test_extract_with_gemini_empty_response(self):
        """Test Gemini extraction with empty response."""
        mock_gemini = Mock()
        mock_gemini.query.return_value = None

        extractor = ArticleExtractor(gemini_api=mock_gemini)
        text, date = extractor.extract_with_gemini("https://example.com")

        assert text is None
        assert date is None

    @patch("web_article_extractor.extractor.requests.get")
    def test_process_csv_with_skip_domains(self, mock_get, tmp_path):  # pylint: disable=unused-argument
        """Test CSV processing with domain skipping."""
        input_csv = tmp_path / "input.csv"
        input_data = pd.DataFrame(
            {
                "id": ["1"],
                "url": ["https://instagram.com/test"],
            }
        )
        input_data.to_csv(input_csv, index=False)

        config = Config(id_column="id", url_columns=["url"], skip_domains=["instagram.com"])
        extractor = ArticleExtractor(gemini_api=Mock())
        output_csv = tmp_path / "output.csv"

        extractor.process_csv(input_csv, output_csv, config)

        # Should create empty output (header only)
        output_data = pd.read_csv(output_csv)
        assert len(output_data) == 0
