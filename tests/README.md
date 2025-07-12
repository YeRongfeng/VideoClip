# Tests for VideoClip application

This directory contains all the test files for the VideoClip application.

## Test Structure

- `test_main.py` - Tests for main application logic
- `test_video_processor.py` - Tests for video processing functionality  
- `test_ui_components.py` - Tests for UI components
- `test_crop_controller.py` - Tests for crop functionality
- `test_utils.py` - Tests for utility functions
- `test_integration.py` - Integration tests

## Running Tests

```bash
# Install test dependencies
uv sync --dev

# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=. --cov-report=html

# Run specific test file
uv run pytest tests/test_utils.py
```

## Test Requirements

- pytest
- pytest-cov
- pytest-mock
- pytest-qt (for GUI testing)
