# Architecture Instructions

## Overview

This document describes the architecture and design of the `web-article-extractor` module, a generic Python package for extracting article text and publication dates from web URLs using a three-stage extraction pipeline.

## Core Design Principles

1. **Generic and Reusable**: The module is designed to work with any CSV containing URLs, not tied to any specific domain or use case
2. **Three-Stage Pipeline**: HTML parsers first (newspaper3k → trafilatura), with LLM (Gemini) as fallback
3. **Structured Logging**: JSON-formatted logs with configurable levels for production observability
4. **Configuration-Driven**: YAML-based configuration for flexibility without code changes
5. **High Code Quality**: Enforces black (line-length=108), isort, pylint 10.0, pytest coverage ≥90%

## Module Structure

```
web-article-extractor/
├── src/
│   └── web_article_extractor/
│       ├── __init__.py
│       ├── cli.py                  # Command-line interface
│       ├── config.py                # Pydantic configuration models
│       ├── extractor.py             # Main extraction logic
│       ├── logger.py                # Structured logging setup
│       ├── models.py                # Data models (ExtractionResult)
│       └── providers/
│           ├── __init__.py
│           ├── base.py              # Abstract provider interface
│           └── gemini.py            # Gemini API implementation
├── tests/
│   ├── __init__.py
│   ├── test_cli.py                  # Tests for CLI module
│   ├── test_config.py               # Tests for config module
│   ├── test_extractor.py            # Tests for extractor module
│   ├── test_logger.py               # Tests for logger module
│   ├── test_models.py               # Tests for models module
│   └── test_providers.py            # Tests for providers module
├── .github/
│   ├── instructions/
│   │   └── architecture.instructions.md
│   └── workflows/
│       └── ci.yml                   # CI/CD pipeline
├── pyproject.toml                   # Project configuration
├── .pre-commit-config.yaml          # Pre-commit hooks with coverage
└── README.md
```

## Component Architecture

### 1. Provider Pattern (`providers/`)

**Purpose**: Abstract LLM API interactions for extensibility

**Design**:
- `BaseAPIProvider`: Abstract base class defining the provider interface
- `GeminiAPI`: Concrete implementation for Google Gemini 2.0 Flash

**Key Methods**:
```python
class BaseAPIProvider(ABC):
    @abstractmethod
    def get_env_key_name(self) -> str:
        """Return environment variable name for API key"""

    @abstractmethod
    def get_default_model(self) -> str:
        """Return default model name"""

    @abstractmethod
    def query(self, prompt: str) -> str:
        """Query the API with a prompt"""
```

**Extension Point**: Add new LLM providers (OpenAI, Anthropic, etc.) by subclassing `BaseAPIProvider`

**Configuration**:
- API Key: Set `GEMINI_API_KEY` environment variable
- Model: `gemini-2.0-flash-exp` (default)
- Temperature: 0 (deterministic)
- Max tokens: 8096

### 2. Configuration System (`config.py`)

**Purpose**: Load CSV column mappings from YAML with Pydantic validation

**Implementation**: Uses Pydantic BaseModel for robust validation

**YAML Schema**:
```yaml
# config.yaml
id_column: rest_id                    # Column name for unique identifiers
url_columns:                          # List of columns containing URLs
  - Web site restaurant
  - Web site Chef
  - Web
```

**Pydantic Model**:
```python
from pydantic import BaseModel, Field, field_validator

class Config(BaseModel):
    id_column: str = Field(..., description="Column name for unique IDs")
    url_columns: list[str] = Field(..., description="URL column names")

    @field_validator("url_columns")
    @classmethod
    def validate_url_columns(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError("url_columns must not be empty")
        return v
```

**Validation**:
- Automatic type checking via Pydantic
- Field validators for business logic
- Required fields enforced by Pydantic
- Clear error messages for validation failures

**Usage**:
```python
from web_article_extractor.config import Config

config = Config.from_yaml("config.yaml")
# config.id_column = "rest_id"
# config.url_columns = ["Web site restaurant", "Web site Chef", "Web"]
```

### 3. Data Models (`models.py`)

**Purpose**: Define data structures for extraction results

**ExtractionResult Dataclass**:
```python
@dataclass
class ExtractionResult:
    """Result of article extraction."""
    id_value: str
    url: str
    extracted_text: str
    publication_date: str | None
    extraction_method: str  # 'newspaper', 'trafilatura', 'gemini', 'none'
    status: str  # 'success' or 'error'
    error_message: str | None = None
```

**Design**: Separate module for clean separation of concerns and reusability

### 4. Three-Stage Extraction Pipeline (`extractor.py`)

**Architecture**: Sequential fallback pattern for robust extraction

**Stage 1: newspaper3k**
- Fast, specialized for news articles
- Extracts text + publish date from HTML
- Success criteria: text length > 100 characters
- Fallback trigger: Extraction failure or insufficient text

**Stage 2: trafilatura**
- Generic web page extractor
- Better handling of diverse site structures
- Extracts text + metadata dates
- Fallback trigger: Extraction failure or insufficient text

**Stage 3: Gemini LLM**
- Ultimate fallback using AI understanding
- Fetches raw HTML and uses Gemini to extract content
- Prompt format: JSON response with `{text, date}` fields
- Cost consideration: Only used when HTML parsers fail

**Date Normalization**:
- All dates converted to ISO 8601 format (YYYY-MM-DD)
- Uses `dateutil.parser` for flexible parsing
- Handles various input formats automatically

**Output Schema**:
```csv
id,url,extracted_text,publication_date,extraction_method,status,error_message
123,https://...,Article text...,2024-01-15,newspaper,success,
124,https://...,Article text...,2024-02-01,trafilatura,success,
125,https://...,Article text...,,gemini,success,
126,https://...,,,,error,All extraction methods failed
```

### 4. Structured Logging (`logger.py`)

**Purpose**: Production-ready observability with machine-readable logs

**Format**: JSON with fields:
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "logger": "web_article_extractor",
  "level": "INFO",
  "message": "Extraction successful",
  "url": "https://example.com",
  "method": "newspaper"
}
```

**Log Levels**:
- **DEBUG**: Detailed extraction attempts, failures
- **INFO**: Successful extractions, CSV processing progress
- **WARNING**: Recoverable issues (e.g., insufficient text)
- **ERROR**: Failed extractions, API errors
- **CRITICAL**: System-level failures

**Configuration**: Set via CLI `--log-level` option

**Usage**:
```python
from web_article_extractor.logger import setup_logger, get_logger

setup_logger("web_article_extractor", "INFO")
logger = get_logger()
logger.info("Starting extraction", extra={"url": url, "id": id_value})
```

### 6. Command-Line Interface (`cli.py`)

**Framework**: Click for robust argument parsing and validation

**Command**:
```bash
web-article-extractor INPUT_CSV --output-csv OUTPUT_CSV --config CONFIG_YAML [--log-level LEVEL]
```

**Arguments and Options**:
- `INPUT_CSV`: Path to CSV with URLs (positional argument, validated for existence)
- `--output-csv`, `-o`: Path for results CSV (required option)
- `--config`, `-c`: Path to configuration file (required option, validated for existence)
- `--log-level`: DEBUG|INFO|WARNING|ERROR|CRITICAL (optional, default: INFO)

**Design Rationale**: Options instead of positional arguments for better clarity and flexibility

**Example**:
```bash
web-article-extractor \
  restaurants.csv \
  --output-csv results.csv \
  --config config.yaml \
  --log-level DEBUG
```

## Data Flow

```
1. User invokes CLI
   ↓
2. Load YAML configuration (column mappings)
   ↓
3. Read input CSV with pandas
   ↓
4. For each row:
   For each URL column:
     ↓
     4a. Try newspaper3k extraction
     ↓ (if failed)
     4b. Try trafilatura extraction
     ↓ (if failed)
     4c. Try Gemini extraction
     ↓
     4d. Normalize date to ISO 8601
     ↓
     4e. Create ExtractionResult
   ↓
5. Write results to output CSV
   ↓
6. Log summary statistics
```

## Development Tooling

### Code Quality Standards

**Black** (line-length=108):
```bash
black --line-length=108 src/ tests/
```

**isort** (profile=black):
```bash
isort --profile=black --line-length=108 src/ tests/
```

**pylint** (score ≥10.0):
```bash
pylint src/web_article_extractor --fail-under=10.0
```

**pyupgrade** (Python 3.13+):
```bash
pyupgrade --py313-plus **/*.py
```

### Testing Strategy

**Coverage Requirement**: ≥90% via pytest-cov (enforced in pre-commit)

**Test Organization**: One test file per source module following Python standards
- [test_cli.py](../../tests/test_cli.py) - CLI interface tests
- [test_config.py](../../tests/test_config.py) - Configuration and Pydantic validation
- [test_extractor.py](../../tests/test_extractor.py) - Extraction pipeline logic
- [test_logger.py](../../tests/test_logger.py) - Logging configuration
- [test_models.py](../../tests/test_models.py) - Data model tests
- [test_providers.py](../../tests/test_providers.py) - API provider tests

**Unit Tests**:
- Config Pydantic validation
- GeminiAPI provider (mocked API calls)
- Date normalization logic
- Individual extraction methods
- Error handling
- CLI option parsing
- Logger setup and configuration

**Test Coverage in Pre-commit**:
- Automatically runs pytest with coverage checks
- Fails if coverage drops below 90%
- Integrated into Git workflow

**Mocking Strategy**:
- Use `pytest-mock` for external dependencies
- Mock `google.generativeai` for Gemini tests
- Mock `newspaper.Article` and `trafilatura` for extraction tests
- Mock `requests.get` for HTTP calls

### CI/CD Pipeline (`.github/workflows/ci.yml`)

**Trigger**: Push/PR to main or develop branches

**Jobs**:
1. **test**: Run pytest with coverage ≥90%
2. **lint**: Run pylint, black, isort checks

**Python Version**: 3.13

**Environment**:
- `GEMINI_API_KEY`: Set via GitHub Secrets (or dummy for tests)

- **pytest-coverage** (≥90% coverage enforced)
### Pre-commit Hooks (`.pre-commit-config.yaml`)

**Hooks**:
- Standard checks: trailing-whitespace, end-of-file-fixer, check-yaml, etc.
- black (line-length=108)
- isort (profile=black, line-length=108)
- pyupgrade (--py313-plus)
- pylint (fail-under=10.0)

**Setup**:
```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

## Extension Points

### Adding New LLM Providers

1. Create new file in `src/web_article_extractor/providers/`
2. Subclass `BaseAPIProvider`
3. Implement required methods:
   - `get_env_key_name()`: Return API key env var name
   - `get_default_model()`: Return default model
   - `_initialize_client()`: Setup API client
   - `query(prompt)`: Execute API call
4. Update `providers/__init__.py` exports
5. Add provider option to CLI or extractor constructor

**Example**:
```python
# providers/openai.py
from .base import BaseAPIProvider
import openai

class OpenAIProvider(BaseAPIProvider):
    def get_env_key_name(self) -> str:
        return "OPENAI_API_KEY"

    def get_default_model(self) -> str:
        return "gpt-4"

    # ... implement other methods
```

### Adding Custom Extraction Methods

1. Add new method to `ArticleExtractor` class
2. Follow naming pattern: `extract_with_<method_name>(url)`
3. Return tuple: `(text: str | None, date: str | None)`
4. Update `extract_from_url()` to include new stage

### Customizing Output Format

**Current**: CSV with fixed schema

**To Add JSON/Parquet**:
1. Add format parameter to `process_csv()` method
2. Create format-specific writers:
   ```python
   def _write_json(self, results, path):
       # Convert ExtractionResult to JSON

   def _write_parquet(self, results, path):
       # Convert ExtractionResult to Parquet
   ```

## Performance Considerations

**Bottlenecks**:
1. HTTP requests (network I/O bound)
2. Gemini API calls (rate limited, expensive)

**Optimization Strategies**:
- Sequential processing minimizes API costs (no parallel Gemini calls)
- HTML parsers first avoid unnecessary LLM usage
- Consider adding async/parallel processing for HTML stages (future)
- Implement request caching for repeated URLs (future)

**Rate Limiting**:
- Gemini free tier: 60 requests/minute
- Current: No rate limiting (sequential processing naturally throttles)
- Future: Add configurable rate limiter

## Error Handling Philosophy

**Fail Gracefully**:
- Individual URL failures don't stop processing
- Errors logged to structured logs + output CSV
- Status field: `success` | `error`
- Error messages captured for debugging

**No Retries**:
- Failed extractions logged immediately
- User can review errors in output CSV
- Manual retry possible by filtering error rows

**Validation**:
- YAML config validated on load (fail fast)
- CSV columns validated before processing (fail fast)
- URL-level errors handled gracefully (continue processing)

## License

**MIT License**: Permissive, allows commercial use, modification, distribution

## Dependencies

**Core**:
- `google-generativeai`: Gemini API client
- `newspaper3k`: News article extraction
- `trafilatura`: Generic web content extraction
- `pydantic`: Configuration validation
- `pydantic-settings`: Settings management
- `pandas`: CSV I/O and data manipulation
- `requests`: HTTP client
- `click`: CLI framework
- `python-json-logger`: Structured logging
- `python-dateutil`: Date parsing

**Development**:
- `pytest`, `pytest-cov`, `pytest-mock`: Testing
- `coverage`: Coverage reporting and enforcement
- `pytest`, `pytest-cov`, `pytest-mock`: Testing
- `black`, `isort`, `pylint`, `pyupgrade`: Code quality
- `pre-commit`: Git hooks

## Configuration Examples

### Basic Configuration
```yaml
id_column: id
url_columns:
  - website_url
```

### Multi-Column Configuration (Restaurant Example)
```yaml
id_column: rest_id
url_columns:
  - Web site restaurant
  - Web site Chef
  - Web
```

## Usage Examples--output-csv output.csv --config config.yaml
```

### With Debug Logging
```bash
web-article-extractor input.csv -o output.csv -c

### With Debug Logging
```bash
web-article-extractor input.csv output.csv config.yaml --log-level DEBUG
```

### Programmatic Usage
```python
from web_article_extractor import ArticleExtractor
from web_article_extractor.config import Config
from web_article_extractor.logger import setup_logger

# Setup
setup_logger("web_article_extractor", "INFO")
config = Config.from_yaml("config.yaml")
extractor = ArticleExtractor()

# Process
extractor.process_csv("input.csv", "output.csv", config)
```

## Future Enhancements

1. **Parallel Processing**: Add async/thread pool for faster extraction
2. **Caching**: Redis/file-based cache for repeated URLs
3. **More Providers**: OpenAI, Anthropic, local models
4. **Custom Parsers**: Plugin system for domain-specific extractors
5. **Output Formats**: JSON, Parquet, database export
6. **Monitoring**: Prometheus metrics, tracing
7. **Rate Limiting**: Configurable limits per provider
8. **Retry Logic**: Exponential backoff for transient failures
