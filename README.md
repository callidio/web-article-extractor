# Web Article Extractor

A generic, production-ready Python module for extracting article text and publication dates from web URLs using a three-stage pipeline: HTML parsers (newspaper3k → trafilatura) with Google Gemini LLM fallback.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Features

- 🎯 **Three-Stage Extraction**: newspaper3k → trafilatura → Gemini LLM fallback
- 📊 **CSV-Based Workflow**: Process multiple URLs from CSV with configurable column mappings
- 🔧 **YAML Configuration**: Flexible column mapping without code changes
- 📝 **Structured Logging**: JSON-formatted logs with CLI-configurable levels
- 📅 **ISO 8601 Dates**: Automatic date normalization to standard format
- 🏗️ **Provider Pattern**: Extensible architecture for adding new LLM providers
- ✅ **High Quality**: Black (108), isort, pylint 10.0, pytest coverage ≥90%
- 🚀 **Production Ready**: Pre-commit hooks, CI/CD, comprehensive tests

## Installation

```bash
# Clone repository
git clone https://github.com/yourusername/web-article-extractor.git
cd web-article-extractor

# Install in development mode
pip install -e ".[dev]"

# Or install from PyPI (when published)
pip install web-article-extractor
```

## Quick Start

### 1. Set up Gemini API Key

```bash
export GEMINI_API_KEY="your-api-key-here"
```

### 2. Create Configuration File

Create `config.yaml`:

```yaml
id_column: rest_id
url_columns:
  - Web site restaurant
  - Web site Chef
  - Web
```

### 3. Run Extraction

```bash
web-article-extractor input.csv --output-csv output.csv --config config.yaml --log-level INFO
```

## Usage Examples

### Command Line

```bash
# Basic usage
web-article-extractor restaurants.csv --output-csv results.csv --config config.yaml

# With debug logging
web-article-extractor input.csv -o output.csv -c config.yaml --log-level DEBUG

# With different log levels
web-article-extractor input.csv --output-csv output.csv --config config.yaml --log-level WARNING
```

### Programmatic Usage

```python
from web_article_extractor import ArticleExtractor
from web_article_extractor.config import Config
from web_article_extractor.logger import setup_logger

# Setup logging
setup_logger("web_article_extractor", "INFO")

# Load configuration
config = Config.from_yaml("config.yaml")

# Create extractor
extractor = ArticleExtractor()

# Process CSV
extractor.process_csv("input.csv", "output.csv", config)
```

## Input/Output Format

### Input CSV

Your CSV should contain:
- One column with unique identifiers (specified in `id_column`)
- One or more columns with URLs (specified in `url_columns`)

Example:

```csv
rest_id,Web site restaurant,Web site Chef
1,https://example.com/restaurant,https://example.com/chef
2,https://test.com/place,
```

### Output CSV

Generated CSV contains:

| Column | Description |
|--------|-------------|
| `id` | The identifier from your input CSV |
| `url` | The URL that was processed |
| `extracted_text` | Extracted article text |
| `publication_date` | ISO 8601 formatted date (YYYY-MM-DD) |
| `extraction_method` | Method used: `newspaper`, `trafilatura`, or `gemini` |
| `status` | `success` or `error` |
| `error_message` | Error details if status is `error` |

## Three-Stage Extraction Pipeline

1. **newspaper3k** (Stage 1)
   - Fast, specialized for news articles
   - Extracts text + publish date
   - Falls back if extraction fails or text < 100 chars

2. **trafilatura** (Stage 2)
   - Generic web page extractor
   - Better for diverse site structures
   - Falls back if extraction fails or text < 100 chars

3. **Google Gemini** (Stage 3)
   - LLM-powered extraction using Gemini 2.0 Flash
   - Ultimate fallback when HTML parsing fails
   - Uses AI to understand and extract content

## Configuration

### YAML Schema

```yaml
# Required: Column name containing unique identifiers
id_column: id

# Required: List of column names containing URLs to extract
url_columns:
  - url_column_1
  - url_column_2
  - url_column_3
```

### Environment Variables

- `GEMINI_API_KEY`: Google Gemini API key (required)

### Logging Levels

- `DEBUG`: Detailed extraction attempts, all stages
- `INFO`: Successful extractions, progress updates (default)
- `WARNING`: Recoverable issues
- `ERROR`: Failed extractions
- `CRITICAL`: System-level failures

## Development

### Setup Development Environment

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run pre-commit on all files
pre-commit run --all-files
```

### Running Tests

```bash
# Run all tests with coverage
pytest

# Run with coverage report
pytest --cov=web_article_extractor --cov-report=html

# Run specific test file
pytest tests/test_unit.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code with black
black --line-length=108 src/ tests/

# Sort imports
isort --profile=black --line-length=108 src/ tests/

# Run pylint
pylint src/web_article_extractor

# Run all checks (via pre-commit)
pre-commit run --all-files
```

## Architecture

The module follows these design principles:

- **Provider Pattern**: Extensible LLM provider system
- **Configuration-Driven**: YAML-based, no hardcoded values
- **Structured Logging**: JSON logs for production observability
- **Three-Stage Pipeline**: HTML parsers first, LLM as fallback
- **ISO 8601 Dates**: Standardized date format

For detailed architecture documentation, see [.github/instructions/architecture.instructions.md](.github/instructions/architecture.instructions.md).

## Extending the Module

### Adding a New LLM Provider

```python
# src/web_article_extractor/providers/openai.py
from .base import BaseAPIProvider
import openai

class OpenAIProvider(BaseAPIProvider):
    def get_env_key_name(self) -> str:
        return "OPENAI_API_KEY"

    def get_default_model(self) -> str:
        return "gpt-4"

    def _initialize_client(self):
        openai.api_key = self.api_key
        return openai

    def query(self, prompt: str) -> str:
        response = self.client.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
```

## Requirements

- Python 3.13+
- google-generativeai
- newspaper3k
- trafilatura
- pyyaml
- pandas
- requests
- click
- python-json-logger
- python-dateutil

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure all tests pass and coverage ≥90%
5. Run pre-commit hooks
6. Submit a pull request

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Acknowledgments

- newspaper3k for fast news article extraction
- trafilatura for robust web content extraction
- Google Gemini for LLM-powered fallback extraction
- Pydantic for robust configuration validation

## Changelog

### 0.1.0 (2026-02-01)

- Initial release
- Three-stage extraction pipeline
- YAML configuration with Pydantic validation
- Structured logging
- CLI interface with options instead of arguments
- Provider pattern for LLM extensibility
- Comprehensive test suite (≥90% coverage)
- One test file per source module following Python standards
