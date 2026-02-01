"""Article extraction with HTML parsing and LLM fallback."""

import json
from pathlib import Path

import pandas as pd
import requests
import trafilatura
from dateutil import parser as date_parser
from newspaper import Article

from .config import Config
from .exceptions import ArticleDownloadError, ArticleParseError, HTMLFetchError, LLMExtractionError
from .logger import get_logger
from .models import ExtractionResult
from .providers.gemini import GeminiAPI

logger = get_logger()


class ArticleExtractor:
    """Extract article text and dates from URLs using multiple methods."""

    def __init__(self, gemini_api: GeminiAPI | None = None):
        """
        Initialize article extractor.

        Args:
            gemini_api: Optional GeminiAPI instance. If None, creates new one.
        """
        self.gemini_api = gemini_api or GeminiAPI()

    def extract_with_newspaper(self, url: str) -> tuple[str | None, str | None]:
        """
        Extract article using newspaper3k.

        Args:
            url: URL to extract

        Returns:
            Tuple of (text, date) or (None, None) if extraction fails
        """
        try:
            article = Article(url)
            article.download()
            article.parse()

            text = article.text.strip() if article.text else None
            date = article.publish_date.isoformat() if article.publish_date else None

            if text and len(text) > 100:  # Minimum text length
                logger.info("Extraction successful", extra={"url": url, "method": "newspaper"})
                return text, date

            logger.debug(
                "Insufficient text from newspaper", extra={"url": url, "text_length": len(text or "")}
            )
            return None, None
        except (ArticleDownloadError, ArticleParseError, ValueError, OSError) as e:
            logger.debug("Newspaper extraction failed", extra={"url": url, "error": str(e)})
            return None, None

    def extract_with_trafilatura(self, url: str) -> tuple[str | None, str | None]:
        """
        Extract article using trafilatura.

        Args:
            url: URL to extract

        Returns:
            Tuple of (text, date) or (None, None) if extraction fails
        """
        try:
            downloaded = trafilatura.fetch_url(url)
            if not downloaded:
                return None, None

            text = trafilatura.extract(downloaded, include_comments=False, include_tables=False)
            metadata = trafilatura.extract_metadata(downloaded)

            date = None
            if metadata and metadata.date:
                date = metadata.date

            if text and len(text) > 100:
                logger.info("Extraction successful", extra={"url": url, "method": "trafilatura"})
                return text, date

            logger.debug(
                "Insufficient text from trafilatura",
                extra={"url": url, "text_length": len(text or "")},
            )
            return None, None
        except (HTMLFetchError, ValueError, OSError) as e:
            logger.debug("Trafilatura extraction failed", extra={"url": url, "error": str(e)})
            return None, None

    def extract_with_gemini(self, url: str) -> tuple[str | None, str | None]:
        """
        Extract article using Gemini LLM.

        Args:
            url: URL to extract

        Returns:
            Tuple of (text, date) or (None, None) if extraction fails
        """
        try:
            # Fetch URL content
            response = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
            response.raise_for_status()
            html_content = response.text

            # Create prompt for Gemini
            prompt = f"""Extract the main article text and publication date from this HTML content.
Return a JSON object with two fields:
- "text": The main article text (not HTML, just the readable text)
- "date": The publication date in any format you can find (or null if not found)

HTML content:
{html_content[:50000]}

Return only valid JSON, no additional text."""

            # Query Gemini
            response_text = self.gemini_api.query(prompt)

            # Parse JSON response
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()

            result = json.loads(response_text)
            text = result.get("text", "").strip()
            date = result.get("date")

            if text and len(text) > 100:
                logger.info("Extraction successful", extra={"url": url, "method": "gemini"})
                return text, date

            logger.warning("Insufficient text from Gemini", extra={"url": url, "text_length": len(text)})
            return None, None
        except (LLMExtractionError, requests.RequestException, json.JSONDecodeError, KeyError) as e:
            logger.error("Gemini extraction failed", extra={"url": url, "error": str(e)})
            return None, None

    def normalize_date(self, date_str: str | None) -> str | None:
        """
        Normalize date to ISO 8601 format.

        Args:
            date_str: Date string in any format

        Returns:
            ISO 8601 formatted date string or None
        """
        if not date_str:
            return None

        try:
            parsed_date = date_parser.parse(date_str)
            return parsed_date.date().isoformat()
        except (ValueError, TypeError) as e:
            logger.debug("Date normalization failed", extra={"date_str": date_str, "error": str(e)})
            return None

    def extract_from_url(self, url: str, id_value: str) -> ExtractionResult:
        """
        Extract article from URL using three-stage pipeline.

        Args:
            url: URL to extract
            id_value: Identifier value for this extraction

        Returns:
            ExtractionResult with extraction details
        """
        if not url or not isinstance(url, str) or not url.strip():
            return ExtractionResult.create_error(
                id_value=id_value, url=url or "", error_message="Empty or invalid URL"
            )

        url = url.strip()
        logger.info("Starting extraction", extra={"url": url, "id": id_value})

        # Stage 1: newspaper3k
        text, date = self.extract_with_newspaper(url)
        if text:
            normalized_date = self.normalize_date(date)
            return ExtractionResult(
                id_value=id_value,
                url=url,
                extracted_text=text,
                publication_date=normalized_date,
                extraction_method="newspaper",
                status="success",
            )

        # Stage 2: trafilatura
        text, date = self.extract_with_trafilatura(url)
        if text:
            normalized_date = self.normalize_date(date)
            return ExtractionResult(
                id_value=id_value,
                url=url,
                extracted_text=text,
                publication_date=normalized_date,
                extraction_method="trafilatura",
                status="success",
            )

        # Stage 3: Gemini
        text, date = self.extract_with_gemini(url)
        if text:
            normalized_date = self.normalize_date(date)
            return ExtractionResult(
                id_value=id_value,
                url=url,
                extracted_text=text,
                publication_date=normalized_date,
                extraction_method="gemini",
                status="success",
            )

        # All methods failed
        logger.error("All extraction methods failed", extra={"url": url, "id": id_value})
        return ExtractionResult.create_error(
            id_value=id_value, url=url, error_message="All extraction methods failed"
        )

    def process_csv(self, input_csv: str | Path, output_csv: str | Path, config: Config) -> None:
        """
        Process CSV file and extract articles from URLs.

        Args:
            input_csv: Path to input CSV file
            output_csv: Path to output CSV file
            config: Configuration with column mappings
        """
        logger.info("Starting CSV processing", extra={"input": str(input_csv), "output": str(output_csv)})

        # Read input CSV
        df = pd.read_csv(input_csv)
        logger.info("CSV loaded", extra={"rows": len(df), "columns": list(df.columns)})

        # Validate columns
        if config.id_column not in df.columns:
            raise ValueError(f"ID column '{config.id_column}' not found in CSV")

        missing_cols = [col for col in config.url_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"URL columns not found in CSV: {missing_cols}")

        # Process each row and URL column
        results = []
        total_urls = len(df) * len(config.url_columns)
        processed = 0

        for _, row in df.iterrows():
            id_value = str(row[config.id_column])

            for url_col in config.url_columns:
                url = row[url_col]
                processed += 1

                logger.info(
                    "Processing URL",
                    extra={"progress": f"{processed}/{total_urls}", "id": id_value, "column": url_col},
                )

                result = self.extract_from_url(url, id_value)
                results.append(result)

        # Create output DataFrame
        output_df = pd.DataFrame(
            [
                {
                    "id": r.id_value,
                    "url": r.url,
                    "extracted_text": r.extracted_text,
                    "publication_date": r.publication_date,
                    "extraction_method": r.extraction_method,
                    "status": r.status,
                    "error_message": r.error_message,
                }
                for r in results
            ]
        )

        # Save output CSV
        output_df.to_csv(output_csv, index=False)
        logger.info(
            "CSV processing complete",
            extra={
                "output": str(output_csv),
                "total": len(results),
                "success": sum(1 for r in results if r.status == "success"),
                "errors": sum(1 for r in results if r.status == "error"),
            },
        )
