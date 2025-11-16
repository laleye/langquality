# Packaging Summary

This document summarizes the packaging and distribution setup for LangQuality.

## Package Information

- **Package Name**: `langquality`
- **Version**: 1.0.0
- **License**: MIT
- **Python Support**: 3.8, 3.9, 3.10, 3.11
- **PyPI URL**: https://pypi.org/project/langquality/
- **TestPyPI URL**: https://test.pypi.org/project/langquality/

## Installation

### From PyPI (Production)

```bash
# Basic installation
pip install langquality

# With development dependencies
pip install langquality[dev]

# With documentation dependencies
pip install langquality[docs]

# With all optional dependencies
pip install langquality[all]
```

### From TestPyPI (Testing)

```bash
pip install --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ \
            langquality
```

### From Source

```bash
git clone https://github.com/langquality/langquality-toolkit.git
cd langquality-toolkit
pip install -e .
```

## Package Structure

```
langquality-1.0.0/
├── langquality/                    # Main package
│   ├── __init__.py
│   ├── __main__.py                # CLI entry point
│   ├── cli.py                     # CLI implementation
│   ├── analyzers/                 # Analysis modules
│   ├── config/                    # Configuration handling
│   ├── data/                      # Data loading
│   ├── language_packs/            # Language pack system
│   │   ├── manager.py
│   │   ├── models.py
│   │   ├── validation.py
│   │   └── packs/                 # Bundled language packs
│   │       ├── fon/               # Fongbe
│   │       ├── fra/               # French
│   │       ├── eng/               # English
│   │       ├── cmp/               # Example pack
│   │       ├── min/               # Minimal pack
│   │       └── _template/         # Template for new packs
│   ├── outputs/                   # Output generation
│   ├── pipeline/                  # Pipeline orchestration
│   ├── recommendations/           # Recommendation engine
│   ├── resources/                 # Shared resources
│   └── utils/                     # Utilities
├── fongbe_quality/                # Legacy package (backward compatibility)
└── langquality-1.0.0.dist-info/   # Package metadata
```

## Entry Points

The package provides two command-line tools:

1. **langquality** - Main CLI (recommended)
   ```bash
   langquality --help
   langquality analyze data.csv --language fon
   langquality pack list
   ```

2. **fongbe-quality** - Legacy CLI (deprecated)
   ```bash
   fongbe-quality --help
   ```

## Optional Dependencies

### Development (`dev`)
- pytest, pytest-cov, pytest-xdist, pytest-benchmark, pytest-mock
- black, isort, flake8, mypy
- bandit, pre-commit
- ipython, ipdb

### Documentation (`docs`)
- sphinx, sphinx-rtd-theme
- myst-parser, sphinx-autodoc-typehints
- mkdocs, mkdocs-material

### Build (`build`)
- build, twine
- setuptools, wheel

### NLP Tools
- `spacy`: SpaCy tokenizer support
- `nltk`: NLTK tokenizer support

## Included Language Packs

The package includes several pre-configured language packs:

1. **Fongbe (fon)** - Full pack with all resources
2. **French (fra)** - Full pack with all resources
3. **English (eng)** - Full pack with all resources
4. **Example (cmp)** - Minimal example pack
5. **Minimal (min)** - Bare minimum configuration
6. **Template (_template)** - Template for creating new packs

## Configuration Files

### setup.py
- Traditional setuptools configuration
- Defines package metadata, dependencies, and entry points
- Includes package data specifications

### pyproject.toml
- Modern Python packaging configuration (PEP 518, 621)
- Defines build system requirements
- Configures development tools (black, mypy, pytest, etc.)
- Specifies optional dependencies

### MANIFEST.in
- Specifies additional files to include in source distribution
- Includes documentation, language packs, and resources
- Excludes test files and development artifacts

## Build System

### Build Backend
- **Backend**: setuptools
- **Build Requirements**: setuptools>=68.0.0, wheel>=0.42.0

### Building the Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build source distribution and wheel
python -m build

# Check the distribution
twine check dist/*

# List contents
python -m zipfile -l dist/langquality-1.0.0-py3-none-any.whl
```

### Build Outputs

- **Wheel**: `langquality-1.0.0-py3-none-any.whl` (binary distribution)
- **Source**: `langquality-1.0.0.tar.gz` (source distribution)

## Distribution

### PyPI Publication

Automated via GitHub Actions:
- Triggered on GitHub release creation
- Builds package on multiple platforms
- Tests installation
- Publishes to PyPI using Trusted Publishers (OIDC)

### TestPyPI Testing

Manual trigger via GitHub Actions:
- Go to Actions → Release workflow
- Click "Run workflow"
- Check "Publish to TestPyPI"

## Version Management

### Current Version: 1.0.0

Version is defined in:
- `setup.py`: `version="1.0.0"`
- `pyproject.toml`: `version = "1.0.0"`

### Updating Version

Use the release preparation script:
```bash
python scripts/prepare_release.py --version 1.1.0
```

Or manually update both files.

## Package Metadata

### Classifiers
- Development Status: Beta
- Intended Audience: Developers, Science/Research, Education
- Topic: AI, Linguistics, Text Processing
- License: MIT
- Programming Language: Python 3.8+
- Operating System: OS Independent
- Natural Language: English, French

### Keywords
nlp, low-resource-languages, data-quality, linguistics, language-packs, text-analysis, dataset-quality, multilingual, language-toolkit

### URLs
- Homepage: https://github.com/langquality/langquality-toolkit
- Documentation: https://langquality.readthedocs.io
- Repository: https://github.com/langquality/langquality-toolkit
- Bug Tracker: https://github.com/langquality/langquality-toolkit/issues
- Changelog: https://github.com/langquality/langquality-toolkit/blob/main/CHANGELOG.md
- Discussions: https://github.com/langquality/langquality-toolkit/discussions

## Quality Assurance

### Pre-publication Checks
- ✓ All tests pass (pytest)
- ✓ Code quality checks pass (flake8, black, mypy)
- ✓ Package builds successfully
- ✓ Twine check passes
- ✓ Installation test passes
- ✓ CLI commands work

### Continuous Integration
- Tests on Linux, macOS, Windows
- Tests on Python 3.8, 3.9, 3.10, 3.11
- Code coverage >80%
- Automated linting and type checking

## Backward Compatibility

### Legacy Support
- `fongbe_quality` package included for backward compatibility
- `fongbe-quality` CLI command available (deprecated)
- Deprecation warnings guide users to new package

### Migration Path
Users can migrate from `fongbe-quality` to `langquality`:
```python
# Old import (still works with deprecation warning)
from fongbe_quality import ...

# New import (recommended)
from langquality import ...
```

## Security

### Trusted Publishers
- Uses GitHub OIDC for PyPI authentication
- No API tokens stored in repository
- Requires 2FA on PyPI account

### Code Scanning
- Bandit for security issues
- Dependabot for dependency updates
- Regular security audits

## Support

### Documentation
- [Installation Guide](./user_guide/installation.md)
- [Quick Start](./quickstart.md)
- [PyPI Publication Guide](./PYPI_PUBLICATION_GUIDE.md)
- [Release Process](./RELEASE_PROCESS.md)

### Community
- GitHub Issues: Bug reports and feature requests
- GitHub Discussions: Questions and community support
- Documentation: Comprehensive guides and API reference

## Maintenance

### Regular Tasks
- Update dependencies quarterly
- Review and merge dependabot PRs
- Monitor PyPI download statistics
- Respond to issues and PRs
- Update documentation as needed

### Release Cadence
- **Patch releases**: As needed for bug fixes
- **Minor releases**: Monthly or as features are ready
- **Major releases**: Annually or for breaking changes

## Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [PEP 517 - Build System](https://peps.python.org/pep-0517/)
- [PEP 621 - Project Metadata](https://peps.python.org/pep-0621/)
- [Setuptools Documentation](https://setuptools.pypa.io/)
- [PyPI Help](https://pypi.org/help/)
