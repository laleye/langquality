# CI/CD and Code Quality Setup

This document describes the continuous integration and code quality infrastructure for LangQuality.

## Overview

The project now has a complete CI/CD pipeline and code quality tooling configured.

## GitHub Actions Workflows

### 1. CI Workflow (`.github/workflows/ci.yml`)

**Triggers**: Push and PR to `main` and `develop` branches

**Features**:
- Tests on multiple operating systems (Ubuntu, macOS, Windows)
- Tests on Python versions 3.8, 3.9, 3.10, 3.11
- Runs pytest with coverage reporting
- Uploads coverage to Codecov
- Installs spaCy models automatically

**Usage**: Automatically runs on every push and pull request

### 2. Lint Workflow (`.github/workflows/lint.yml`)

**Triggers**: Push and PR to `main` and `develop` branches

**Features**:
- Code formatting check with Black
- Import sorting check with isort
- Linting with flake8
- Type checking with mypy

**Usage**: Automatically runs on every push and pull request

### 3. Release Workflow (`.github/workflows/release.yml`)

**Triggers**: 
- GitHub release publication
- Manual workflow dispatch

**Features**:
- Builds distribution packages (wheel and source)
- Validates packages with twine
- Publishes to PyPI on release
- Supports TestPyPI for testing

**Usage**: 
- Automatic: Triggered when a GitHub release is published
- Manual: Can be triggered via GitHub Actions UI for TestPyPI

### 4. Documentation Workflow (`.github/workflows/docs.yml`)

**Triggers**: 
- Push to `main` branch
- PR to `main` branch
- Manual workflow dispatch

**Features**:
- Builds Sphinx documentation
- Uploads documentation artifacts
- Deploys to GitHub Pages (on main branch)

**Usage**: Automatically builds docs on every push to main

## Code Quality Tools

### pytest (`pytest.ini`)

**Configuration**:
- Minimum coverage: 80%
- Coverage reports: terminal, HTML, XML
- Test markers: unit, integration, slow, requires_spacy, requires_nltk

**Usage**:
```bash
pytest                    # Run all tests
pytest --cov             # Run with coverage
pytest -m unit           # Run only unit tests
make test                # Via Makefile
make test-cov            # With coverage
```

### Black (`pyproject.toml`)

**Configuration**:
- Line length: 100 characters
- Target Python versions: 3.8-3.11

**Usage**:
```bash
black src/ tests/        # Format code
black --check src/       # Check formatting
make format              # Via Makefile
```

### isort (`pyproject.toml`)

**Configuration**:
- Profile: black (compatible with Black)
- Line length: 100 characters

**Usage**:
```bash
isort src/ tests/        # Sort imports
isort --check-only src/  # Check sorting
make format              # Via Makefile
```

### flake8 (`.flake8`)

**Configuration**:
- Max line length: 127 characters
- Max complexity: 10
- Ignores: E203, E501, W503 (Black compatibility)

**Usage**:
```bash
flake8 src/ tests/       # Run linting
make lint                # Via Makefile
```

### mypy (`mypy.ini`)

**Configuration**:
- Python version: 3.8
- Ignore missing imports: True
- Various strictness settings

**Usage**:
```bash
mypy src/langquality     # Type check
make type-check          # Via Makefile
```

### pre-commit (`.pre-commit-config.yaml`)

**Hooks**:
- General file checks (trailing whitespace, EOF, etc.)
- Black formatting
- isort import sorting
- flake8 linting
- mypy type checking
- bandit security checks
- Markdown and YAML linting

**Usage**:
```bash
pre-commit install           # Install hooks
pre-commit run --all-files   # Run on all files
make pre-commit              # Via Makefile
```

## Development Dependencies

All development tools are listed in `requirements-dev.txt`:

```bash
pip install -r requirements-dev.txt
```

Includes:
- Testing: pytest, pytest-cov, pytest-xdist, pytest-mock
- Formatting: black, isort
- Linting: flake8 with plugins
- Type checking: mypy with type stubs
- Security: bandit
- Pre-commit: pre-commit
- Documentation: sphinx, sphinx-rtd-theme
- Build: build, twine, setuptools, wheel

## Makefile Commands

Convenient commands for common tasks:

```bash
make help           # Show all commands
make install        # Install package in dev mode
make install-dev    # Install with dev dependencies
make test           # Run tests
make test-cov       # Run tests with coverage
make lint           # Run linting checks
make format         # Format code
make type-check     # Run type checking
make pre-commit     # Install and run pre-commit
make clean          # Clean build artifacts
make docs           # Build documentation
make build          # Build distribution packages
```

## Coverage Requirements

- **Minimum**: 80% code coverage
- **Reports**: Generated in `htmlcov/` directory
- **CI**: Coverage uploaded to Codecov on Ubuntu + Python 3.10

## Configuration Files

| File | Purpose |
|------|---------|
| `pytest.ini` | Pytest configuration |
| `.flake8` | Flake8 linting rules |
| `mypy.ini` | Mypy type checking settings |
| `pyproject.toml` | Modern Python project config (Black, isort, coverage, build) |
| `.pre-commit-config.yaml` | Pre-commit hooks configuration |
| `.yamllint.yml` | YAML linting rules |
| `requirements-dev.txt` | Development dependencies |
| `Makefile` | Development task automation |

## Documentation

- **Development Guide**: `docs/development.md` - Comprehensive development documentation
- **Quick Reference**: `DEVELOPMENT.md` - Quick reference for common tasks

## Next Steps

1. **Enable GitHub Actions**: Ensure GitHub Actions are enabled in repository settings
2. **Configure Codecov**: Add Codecov token to repository secrets (optional)
3. **Setup PyPI**: Configure PyPI credentials for releases
4. **Enable GitHub Pages**: Enable GitHub Pages in repository settings for documentation

## Maintenance

### Updating Dependencies

```bash
# Update pre-commit hooks
pre-commit autoupdate

# Update Python dependencies
pip install --upgrade -r requirements-dev.txt
```

### Adding New Checks

1. Add to `.pre-commit-config.yaml` for local checks
2. Add to `.github/workflows/lint.yml` for CI checks
3. Update `Makefile` for convenience commands
4. Document in `docs/development.md`

## Troubleshooting

### CI Failures

1. Check the workflow logs in GitHub Actions
2. Reproduce locally: `make lint && make test-cov`
3. Fix issues and push again

### Pre-commit Hook Failures

1. Review error messages
2. Run `make format` to auto-fix formatting
3. Fix remaining issues manually
4. Stage changes and commit again

### Coverage Below 80%

1. Run `make test-cov` to see coverage report
2. Open `htmlcov/index.html` to see detailed coverage
3. Add tests for uncovered code
4. Re-run tests to verify

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [pytest Documentation](https://docs.pytest.org/)
- [Black Documentation](https://black.readthedocs.io/)
- [pre-commit Documentation](https://pre-commit.com/)
