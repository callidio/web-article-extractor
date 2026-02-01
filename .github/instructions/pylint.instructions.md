# Pylint Instructions

## General Guidelines

The project enforces a **pylint score of 10.0** as part of the pre-commit hooks and CI/CD pipeline. All code must pass pylint checks before being committed.

## Rules for Source Files (`src/`)

**In source files, you should FIX pylint warnings, not disable them.**

- Refactor code to address the root cause of warnings
- Improve code quality by following pylint's suggestions
- Use proper error handling with specific exception types
- Avoid broad exception catches when possible
- Remove unused imports and variables
- Follow naming conventions and best practices

### Exception: Click Decorators

The **only** acceptable pylint disable comment in source files is for Click's decorator pattern in the main CLI entry point:

```python
if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
```

This is necessary because Click decorators inject arguments at runtime, which pylint cannot detect statically.

## Rules for Test Files (`tests/`)

**In test files, you CAN disable pylint warnings** when they don't apply to test code patterns:

- `E0401` (import-error) for test frameworks like pytest
- `W0611` (unused-import) for fixtures and test utilities
- `W0612` (unused-variable) for variables used in assertions
- `W0613` (unused-argument) for mock/fixture parameters
- `R0801` (duplicate-code) for similar test patterns

**Use inline disable comments** for specific issues:

```python
import pytest  # pylint: disable=unused-import

def test_something(mock_fixture):  # pylint: disable=unused-argument
    result = calculate()  # pylint: disable=unused-variable
    assert True
```

**Note**: Tests are checked by pylint but specific warnings can be disabled when they don't apply to test patterns.

## Common Fixable Issues

### Broad Exception Catches

❌ **Bad** (in src files):
```python
try:
    risky_operation()
except Exception as e:  # Too broad!
    handle_error(e)
```

✅ **Good**:
```python
try:
    risky_operation()
except (ValueError, KeyError) as e:  # Specific exceptions
    handle_error(e)
```

✅ **Acceptable** (with justification):
```python
try:
    risky_operation()
except Exception as e:  # pylint: disable=broad-exception-caught
    # Justified: External library may raise any exception type
    logger.error("Unexpected error", extra={"error": str(e)})
```

### Unused Imports

❌ **Bad**:
```python
from pathlib import Path  # Imported but never used
```

✅ **Good**: Remove the import or use it.

### Line Length

Maximum line length is **108 characters**.

❌ **Bad**:
```python
logger.debug("Very long message with lots of context", extra={"url": url, "id": id, "status": status, "timestamp": timestamp})
```

✅ **Good**:
```python
logger.debug(
    "Very long message with lots of context",
    extra={"url": url, "id": id, "status": status, "timestamp": timestamp},
)
```

## Pre-commit Configuration

Pylint is configured in [.pre-commit-config.yaml](../../.pre-commit-config.yaml):

```yaml
- repo: local
  hooks:
    - id: pylint
      name: pylint
      entry: pylint
      language: system
      types: [python]
      args:
        - "--fail-under=10.0"
        - "--max-line-length=108"
```

Pylint runs on all Python files including tests, using the system environment to avoid redundant dependency installations.

## Running Pylint Manually

Check source files:
```bash
pylint src/web_article_extractor --fail-under=10.0
```

Check specific file:
```bash
pylint src/web_article_extractor/extractor.py
```

Get detailed report:
```bash
pylint src/web_article_extractor --reports=y
```

## Summary

- **Source files**: Fix warnings, don't disable (except Click main entry point)
- **Test files**: Can disable specific warnings for test patterns (mocks, fixtures, unused arguments)
- **Target score**: 10.0/10.0
- **Max line length**: 108 characters
- **Philosophy**: Write clean, maintainable code that passes linting with minimal exceptions
