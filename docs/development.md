# Development Guide

This guide covers the development workflow, code quality standards, and testing practices for LangQuality.

## Setup Development Environment

### 1. Clone the Repository

```bash
git clone https://github.com/langquality/langquality-toolkit.git
cd langquality-toolkit
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Development Dependencies

```bash
make install-dev
# Or manually:
pip install -e .
pip install -r requirements-dev.txt
```

### 4. Install Pre-commit Hooks

```bash
pre-commit install
```

## Code Quality Standards

### Code Formatting

We use **Black** for code formatting with a line length of 100 characters:

```bash
# Check formatting
black --check src/ tests/

# Auto-format code
black src/ tests/
# Or use make command
make format
```

### Import Sorting

We use **isort** with Black-compatible settings:

```bash
# Check import sorting
isort --check-only src/ tests/

# Auto-sort imports
isort src/ tests/
```

### Linting

We use **flake8** for linting:

```bash
# Run linting
flake8 src/ tests/
# Or use make command
make lint
```

Configuration is in `.flake8` file. Key rules:
- Max line length: 127 characters
- Max complexity: 10
- Ignores E203, W503 (Black compatibility)

### Type Checking

We use **mypy** for static type checking:

```bash
# Run type checking
mypy src/langquality --ignore-missing-imports
# Or use make command
make type-check
```

Configuration is in `mypy.ini` file.

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=langquality --cov=fongbe_quality

# Run specific test file
pytest tests/unit/test_analyzers.py

# Run with verbose output
pytest -v

# Use make commands
make test
make test-cov
```

### Test Organization

Tests are organized in the `tests/` directory:

```
tests/
├── unit/              # Unit tests for individual components
├── integration/       # Integration tests for workflows
├── fixtures/          # Test fixtures and sample data
└── data/             # Test datasets
```

### Test Markers

Use pytest markers to categorize tests:

```python
@pytest.mark.unit
def test_something():
    pass

@pytest.mark.integration
def test_workflow():
    pass

@pytest.mark.slow
def test_large_dataset():
    pass

@pytest.mark.requires_spacy
def test_with_spacy():
    pass
```

Run specific markers:

```bash
pytest -m unit
pytest -m "not slow"
```

### Coverage Requirements

- Minimum coverage: **80%**
- Coverage reports are generated in `htmlcov/` directory
- View HTML report: `open htmlcov/index.html`

## Pre-commit Hooks

Pre-commit hooks run automatically before each commit. They include:

- Trailing whitespace removal
- End-of-file fixer
- YAML/JSON validation
- Black formatting
- isort import sorting
- flake8 linting
- mypy type checking
- Security checks with bandit

### Manual Pre-commit Run

```bash
# Run on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files

# Skip hooks for a commit (not recommended)
git commit --no-verify
```

## Continuous Integration

### GitHub Actions Workflows

We have four CI workflows:

1. **CI** (`.github/workflows/ci.yml`)
   - Runs tests on multiple OS (Ubuntu, macOS, Windows)
   - Tests Python 3.8, 3.9, 3.10, 3.11
   - Uploads coverage to Codecov

2. **Lint** (`.github/workflows/lint.yml`)
   - Checks code formatting with Black
   - Checks import sorting with isort
   - Runs flake8 linting
   - Runs mypy type checking

3. **Release** (`.github/workflows/release.yml`)
   - Builds distribution packages
   - Publishes to PyPI on release
   - Supports TestPyPI for testing

4. **Documentation** (`.github/workflows/docs.yml`)
   - Builds Sphinx documentation
   - Deploys to GitHub Pages

### Running CI Checks Locally

Before pushing, run all CI checks locally:

```bash
# Format code
make format

# Run linting
make lint

# Run type checking
make type-check

# Run tests with coverage
make test-cov

# Or run all pre-commit hooks
make pre-commit
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/my-new-feature
# or
git checkout -b fix/bug-description
```

### 2. Make Changes

- Write code following our style guide
- Add tests for new functionality
- Update documentation as needed

### 3. Run Quality Checks

```bash
make format      # Format code
make lint        # Check linting
make type-check  # Check types
make test-cov    # Run tests with coverage
```

### 4. Commit Changes

```bash
git add .
git commit -m "feat: add new feature"
# Pre-commit hooks will run automatically
```

### 5. Push and Create PR

```bash
git push origin feature/my-new-feature
```

Then create a Pull Request on GitHub.

## Commit Message Convention

We follow conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Examples:
```
feat: add support for Arabic language pack
fix: resolve tokenization issue with RTL scripts
docs: update language pack creation guide
test: add integration tests for plugin system
```

## Building and Packaging

### Build Distribution

```bash
# Build source and wheel distributions
python -m build
# Or use make command
make build
```

### Test Installation

```bash
# Install from local build
pip install dist/langquality-1.0.0-py3-none-any.whl

# Test the CLI
langquality --version
```

### Publish to TestPyPI

```bash
twine upload --repository testpypi dist/*
```

## Documentation

### Building Documentation

```bash
cd docs
make html
# Or from root
make docs
```

View documentation: `open docs/_build/html/index.html`

### Documentation Standards

- All public APIs must have docstrings
- Use Google-style docstrings
- Include examples in docstrings
- Keep documentation up-to-date with code changes

Example docstring:

```python
def analyze_sentences(sentences: List[Sentence], language_pack: LanguagePack) -> AnalysisResults:
    """Analyze a list of sentences using the specified language pack.
    
    Args:
        sentences: List of Sentence objects to analyze
        language_pack: LanguagePack containing configuration and resources
    
    Returns:
        AnalysisResults object containing metrics and recommendations
    
    Raises:
        AnalyzerError: If analysis fails
    
    Example:
        >>> pack = LanguagePackManager().load_language_pack('fon')
        >>> sentences = load_sentences('data.csv')
        >>> results = analyze_sentences(sentences, pack)
    """
    pass
```

## Troubleshooting

### Pre-commit Hook Failures

If pre-commit hooks fail:

1. Review the error messages
2. Fix the issues manually or let auto-fixers handle them
3. Stage the changes: `git add .`
4. Commit again

### Test Failures

If tests fail:

1. Run the specific failing test: `pytest tests/path/to/test.py::test_name -v`
2. Check the error message and stack trace
3. Fix the issue
4. Re-run tests

### Import Errors

If you get import errors:

1. Ensure you're in the virtual environment
2. Reinstall in development mode: `pip install -e .`
3. Check that all dependencies are installed: `pip install -r requirements-dev.txt`

## Getting Help

- Check the [User Guide](user_guide.md)
- Read the [API Reference](api_reference/)
- Ask questions in [GitHub Discussions](https://github.com/langquality/langquality-toolkit/discussions)
- Report bugs in [GitHub Issues](https://github.com/langquality/langquality-toolkit/issues)
