# Development Quick Reference

Quick reference for common development tasks in LangQuality.

## Quick Setup

```bash
# Clone and setup
git clone https://github.com/langquality/langquality.git
cd langquality
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
make install-dev
```

## Common Commands

### Testing
```bash
make test           # Run all tests
make test-cov       # Run tests with coverage
pytest -v           # Verbose test output
pytest -k "test_name"  # Run specific test
```

### Code Quality
```bash
make format         # Auto-format code (black + isort)
make lint           # Check linting (flake8)
make type-check     # Type checking (mypy)
make pre-commit     # Run all pre-commit hooks
```

### Development
```bash
make install        # Install package in dev mode
make clean          # Clean build artifacts
make build          # Build distribution packages
make docs           # Build documentation
```

## Code Quality Standards

- **Line Length**: 100 characters (Black), 127 max (flake8)
- **Test Coverage**: Minimum 80%
- **Python Versions**: 3.8, 3.9, 3.10, 3.11
- **Type Hints**: Encouraged but not required

## Pre-commit Hooks

Automatically run on commit:
- ✓ Black formatting
- ✓ isort import sorting
- ✓ flake8 linting
- ✓ mypy type checking
- ✓ YAML/JSON validation
- ✓ Security checks (bandit)

Skip hooks (not recommended):
```bash
git commit --no-verify
```

## Testing Markers

```python
@pytest.mark.unit           # Unit tests
@pytest.mark.integration    # Integration tests
@pytest.mark.slow           # Slow tests
@pytest.mark.requires_spacy # Needs spaCy models
```

Run specific markers:
```bash
pytest -m unit
pytest -m "not slow"
```

## Commit Convention

```
feat: Add new feature
fix: Fix bug
docs: Update documentation
style: Format code
refactor: Refactor code
test: Add/update tests
chore: Maintenance
```

## CI/CD Workflows

- **CI**: Tests on Ubuntu, macOS, Windows (Python 3.8-3.11)
- **Lint**: Code quality checks
- **Release**: PyPI publishing
- **Docs**: Documentation building and deployment

## File Structure

```
.
├── src/
│   ├── langquality/        # Main package
│   └── fongbe_quality/     # Legacy package (deprecated)
├── tests/
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── fixtures/           # Test fixtures
├── docs/                   # Documentation
├── .github/workflows/      # CI/CD workflows
├── pytest.ini              # Pytest config
├── pyproject.toml          # Project config
├── .flake8                 # Flake8 config
├── mypy.ini                # Mypy config
└── .pre-commit-config.yaml # Pre-commit config
```

## Troubleshooting

### Import errors
```bash
pip install -e .
```

### Pre-commit failures
```bash
make format  # Auto-fix formatting
git add .
git commit
```

### Test failures
```bash
pytest tests/path/to/test.py::test_name -v
```

## Resources

- [Full Development Guide](docs/development.md)
- [Contributing Guidelines](CONTRIBUTING.md)
- [GitHub Discussions](https://github.com/langquality/langquality/discussions)
- [Issue Tracker](https://github.com/langquality/langquality/issues)
