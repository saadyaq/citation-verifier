# Tests

This directory contains the test suite for the citation-verifier project.

## Structure

```
tests/
├── citation_verifier/    # Tests for core citation_verifier module
├── extractors/           # Tests for claim extraction
├── parsers/              # Tests for document parsers
└── fixtures/             # Test data files
```

## Running Tests

### Run all tests
```bash
pytest
```

### Run tests for a specific module
```bash
pytest tests/parsers/
pytest tests/extractors/
pytest tests/citation_verifier/
```

### Run a specific test file
```bash
pytest tests/parsers/test_markdown.py
```

### Run tests with specific markers
```bash
# Skip slow tests
pytest -m "not slow"

# Run only API tests
pytest -m api
```

### Run tests with coverage
```bash
pytest --cov=src --cov-report=html
```

## Test Categories

- **Unit tests**: Test individual functions and classes in isolation
- **Integration tests**: Test how components work together
- **API tests**: Tests that make real API calls (marked with `@pytest.mark.api`)

## Notes

- Some tests require the `ANTHROPIC_API_KEY` environment variable
- API tests are skipped by default to avoid unnecessary API calls
- Tests that require real network calls are marked appropriately
- Mock objects should be used where possible to avoid external dependencies
