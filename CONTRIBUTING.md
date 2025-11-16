# Contributing to LangQuality

Thank you for your interest in contributing to LangQuality! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Language Pack Contributions](#language-pack-contributions)
- [Community](#community)

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## Getting Started

### Ways to Contribute

There are many ways to contribute to LangQuality:

- **Report bugs**: Submit detailed bug reports with reproducible examples
- **Suggest features**: Propose new features or enhancements
- **Write code**: Fix bugs, implement features, or improve performance
- **Create language packs**: Add support for new languages
- **Improve documentation**: Fix typos, clarify instructions, add examples
- **Write tutorials**: Create guides, blog posts, or video tutorials
- **Answer questions**: Help other users in GitHub Discussions
- **Review pull requests**: Provide feedback on proposed changes

### First-Time Contributors

If you're new to open source or LangQuality, look for issues labeled:
- `good first issue`: Simple issues perfect for newcomers
- `help wanted`: Issues where we need community help
- `documentation`: Documentation improvements

## How to Contribute

### Reporting Bugs

Before submitting a bug report:
1. Check the [existing issues](https://github.com/langquality/langquality/issues) to avoid duplicates
2. Verify the bug exists in the latest version
3. Collect relevant information (version, OS, configuration, error messages)

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md) and include:
- Clear description of the bug
- Steps to reproduce
- Expected vs. actual behavior
- Environment details
- Error messages and logs
- Minimal reproducible example

### Suggesting Features

Before suggesting a feature:
1. Check if it's already been proposed
2. Consider if it aligns with the project's goals
3. Think about how it would benefit the community

Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md) and include:
- Clear description of the feature
- Problem it solves
- Proposed solution
- Use cases and examples
- Implementation considerations

### Asking Questions

For questions about using LangQuality:
- Check the [documentation](docs/)
- Search [GitHub Discussions](https://github.com/langquality/langquality/discussions)
- Ask in the Q&A category of Discussions

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment tool (venv, conda, or virtualenv)

### Setting Up Your Development Environment

1. **Fork the repository** on GitHub

2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/langquality.git
   cd langquality
   ```

3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/langquality/langquality.git
   ```

4. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

5. **Install in development mode**:
   ```bash
   pip install -e .[dev]
   ```

6. **Install pre-commit hooks** (optional but recommended):
   ```bash
   pre-commit install
   ```

7. **Verify installation**:
   ```bash
   langquality --version
   pytest tests/
   ```

### Keeping Your Fork Updated

```bash
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:
- Line length: 100 characters (not 79)
- Use double quotes for strings
- Use type hints for function signatures

### Code Formatting

We use **Black** for code formatting:
```bash
black src/ tests/
```

### Linting

We use **flake8** for linting:
```bash
flake8 src/ tests/
```

Configuration in `.flake8`:
```ini
[flake8]
max-line-length = 100
extend-ignore = E203, W503
exclude = .git,__pycache__,build,dist
```

### Type Checking

We use **mypy** for static type checking:
```bash
mypy src/
```

### Code Structure

- **Modularity**: Keep functions and classes focused and single-purpose
- **Documentation**: Add docstrings to all public functions and classes
- **Type hints**: Use type hints for function parameters and return values
- **Error handling**: Use appropriate exceptions and provide helpful error messages
- **Logging**: Use the logging module instead of print statements

### Docstring Format

Use Google-style docstrings:

```python
def analyze_sentences(sentences: List[Sentence], config: AnalysisConfig) -> AnalysisResults:
    """Analyze a list of sentences for quality metrics.
    
    Args:
        sentences: List of Sentence objects to analyze
        config: Configuration for analysis parameters
        
    Returns:
        AnalysisResults object containing metrics and recommendations
        
    Raises:
        ValueError: If sentences list is empty
        ConfigurationError: If config is invalid
        
    Example:
        >>> sentences = load_sentences("data.csv")
        >>> config = AnalysisConfig(language="fon")
        >>> results = analyze_sentences(sentences, config)
    """
    pass
```

## Testing Guidelines

### Running Tests

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=langquality --cov-report=html
```

Run specific test file:
```bash
pytest tests/unit/test_analyzers.py
```

### Writing Tests

- **Coverage**: Aim for >80% code coverage
- **Test structure**: Use the Arrange-Act-Assert pattern
- **Fixtures**: Use pytest fixtures for common test data
- **Naming**: Use descriptive test names: `test_<function>_<scenario>_<expected_result>`
- **Isolation**: Tests should be independent and not rely on execution order

Example test:

```python
def test_structural_analyzer_identifies_short_sentences():
    """Test that StructuralAnalyzer correctly identifies sentences that are too short."""
    # Arrange
    config = AnalysisConfig(min_words=3)
    analyzer = StructuralAnalyzer(config)
    sentences = [
        Sentence(text="Hi", domain="test", source_file="test.csv", line_number=1),
        Sentence(text="This is good", domain="test", source_file="test.csv", line_number=2),
    ]
    
    # Act
    results = analyzer.analyze(sentences)
    
    # Assert
    assert results.issues_found == 1
    assert "too short" in results.issues[0].description.lower()
```

### Test Organization

```
tests/
├── unit/              # Unit tests for individual components
├── integration/       # Integration tests for workflows
├── fixtures/          # Test data and fixtures
└── conftest.py        # Shared pytest configuration
```

## Documentation

### Documentation Structure

- **User documentation**: `docs/` - Guides for end users
- **API documentation**: Generated from docstrings using Sphinx
- **README**: Project overview and quick start
- **CHANGELOG**: Version history and changes

### Writing Documentation

- Use clear, concise language
- Include code examples
- Add screenshots or diagrams where helpful
- Keep documentation up-to-date with code changes
- Use proper Markdown formatting

### Building Documentation

```bash
cd docs/
make html
```

View at `docs/_build/html/index.html`

## Submitting Changes

### Branch Naming

Use descriptive branch names:
- `feature/add-swahili-pack`
- `fix/tokenization-bug`
- `docs/update-quickstart`
- `refactor/analyzer-base-class`

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(analyzers): add tone analyzer for tonal languages

Implements a new analyzer that detects tone patterns in languages
with lexical tone systems.

Closes #123
```

```
fix(loader): handle UTF-8 BOM in CSV files

The CSV loader now correctly handles files with UTF-8 BOM markers.

Fixes #456
```

### Pull Request Process

1. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make your changes** following the coding standards

3. **Write tests** for your changes

4. **Update documentation** as needed

5. **Run tests and linting**:
   ```bash
   pytest
   black src/ tests/
   flake8 src/ tests/
   mypy src/
   ```

6. **Commit your changes** with clear commit messages

7. **Push to your fork**:
   ```bash
   git push origin feature/my-feature
   ```

8. **Create a pull request** on GitHub using the [PR template](.github/PULL_REQUEST_TEMPLATE.md)

9. **Respond to review feedback** and make requested changes

10. **Wait for approval** from maintainers

### Pull Request Checklist

Before submitting, ensure:
- [ ] Code follows project style guidelines
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Documentation updated
- [ ] CHANGELOG.md updated (for significant changes)
- [ ] Commit messages follow conventions
- [ ] PR description is clear and complete

## Language Pack Contributions

### Creating a Language Pack

1. **Use the template**:
   ```bash
   langquality pack create <language_code>
   ```

2. **Fill in the configuration** (`config.yaml`)

3. **Add linguistic resources** to `resources/`

4. **Create metadata** (`metadata.json`)

5. **Write a README** with language-specific information

6. **Test the pack**:
   ```bash
   langquality pack validate language_packs/<language_code>/
   langquality analyze --language <language_code> test_data.csv
   ```

7. **Submit using the [language pack template](.github/ISSUE_TEMPLATE/language_pack_submission.md)**

### Language Pack Guidelines

- Use ISO 639-3 language codes
- Provide proper attribution for all resources
- Ensure licenses are compatible (MIT, CC-BY, or similar)
- Include example data for testing
- Document any language-specific considerations
- Follow the standard directory structure

See [docs/language_pack_guide.md](docs/language_pack_guide.md) for detailed instructions.

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions, ideas, and general discussion
- **Pull Requests**: Code review and collaboration

### Getting Help

- Read the [documentation](docs/)
- Search [existing issues](https://github.com/langquality/langquality/issues)
- Ask in [GitHub Discussions](https://github.com/langquality/langquality/discussions)
- Check the [FAQ](docs/faq.md)

### Recognition

Contributors are recognized in:
- CHANGELOG.md for their contributions
- README.md contributors section
- Language pack metadata files
- Release notes

## License

By contributing to LangQuality, you agree that your contributions will be licensed under the MIT License.

## Questions?

If you have questions about contributing, please:
1. Check this guide and the documentation
2. Search existing issues and discussions
3. Ask in GitHub Discussions
4. Contact the maintainers

Thank you for contributing to LangQuality! 🎉
