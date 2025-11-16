# Installation Guide

This guide covers all installation methods for LangQuality and its dependencies.

## System Requirements

### Minimum Requirements

- **Operating System**: Linux, macOS, or Windows
- **Python**: 3.8 or higher
- **RAM**: 2GB minimum, 4GB recommended
- **Disk Space**: 500MB for base installation, additional space for language models

### Recommended Setup

- **Python**: 3.10 or 3.11 (best compatibility)
- **RAM**: 4GB or more for large datasets
- **Disk Space**: 2GB for multiple language packs

## Installation Methods

### Method 1: Install from PyPI (Recommended)

The simplest way to install LangQuality:

```bash
pip install langquality
```

Verify installation:

```bash
langquality --version
```

### Method 2: Install from Source

For development or latest features:

```bash
# Clone the repository
git clone https://github.com/langquality/langquality-toolkit.git
cd langquality-toolkit

# Install in development mode
pip install -e .

# Or install normally
pip install .
```

### Method 3: Install with Optional Dependencies

Install with all optional features:

```bash
# Install with all extras
pip install langquality[all]

# Install specific extras
pip install langquality[dev]      # Development tools
pip install langquality[docs]     # Documentation tools
pip install langquality[spacy]    # spaCy support
```

## Virtual Environment Setup

### Using venv (Recommended)

```bash
# Create virtual environment
python -m venv langquality-env

# Activate on Linux/Mac
source langquality-env/bin/activate

# Activate on Windows
langquality-env\Scripts\activate

# Install LangQuality
pip install langquality
```

### Using conda

```bash
# Create conda environment
conda create -n langquality python=3.10

# Activate environment
conda activate langquality

# Install LangQuality
pip install langquality
```

## Language Pack Dependencies

Some language packs require additional dependencies.

### spaCy Models

For languages using spaCy tokenization:

```bash
# French
python -m spacy download fr_core_news_md

# English
python -m spacy download en_core_web_md

# Spanish
python -m spacy download es_core_news_md
```

### NLTK Data

For languages using NLTK:

```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

## Verifying Installation

### Check Installation

```bash
# Check version
langquality --version

# List available commands
langquality --help

# List installed language packs
langquality pack list
```

### Run Test Analysis

```bash
# Download test data
curl -O https://raw.githubusercontent.com/langquality/langquality-toolkit/main/tests/data/test_sample.csv

# Run analysis
langquality analyze -i test_sample.csv -o test_output --language eng

# Check output
ls test_output/
```

Expected output files:
- `dashboard.html`
- `analysis_results.json`
- `annotated_sentences.csv`

## Troubleshooting

### Common Issues

#### Issue: `command not found: langquality`

**Cause**: Installation directory not in PATH

**Solution**:
```bash
# Find where pip installed the package
pip show langquality

# Add to PATH (Linux/Mac)
export PATH="$HOME/.local/bin:$PATH"

# Or use python -m
python -m langquality --help
```

#### Issue: `ModuleNotFoundError: No module named 'langquality'`

**Cause**: Package not installed or wrong Python environment

**Solution**:
```bash
# Check Python version
python --version

# Reinstall
pip install --force-reinstall langquality

# Or check if in correct virtual environment
which python
```

#### Issue: `OSError: [E050] Can't find model 'fr_core_news_md'`

**Cause**: spaCy model not downloaded

**Solution**:
```bash
python -m spacy download fr_core_news_md
```

#### Issue: `PermissionError` during installation

**Cause**: Insufficient permissions

**Solution**:
```bash
# Install for user only
pip install --user langquality

# Or use virtual environment (recommended)
python -m venv venv
source venv/bin/activate
pip install langquality
```

### Platform-Specific Issues

#### Windows

If you encounter SSL errors:

```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org langquality
```

#### macOS

If you have multiple Python versions:

```bash
# Use specific Python version
python3.10 -m pip install langquality
```

#### Linux

If you need system-wide installation:

```bash
sudo pip install langquality
```

## Upgrading

### Upgrade to Latest Version

```bash
pip install --upgrade langquality
```

### Upgrade Specific Version

```bash
pip install langquality==1.2.0
```

### Check for Updates

```bash
pip list --outdated | grep langquality
```

## Uninstallation

### Remove LangQuality

```bash
pip uninstall langquality
```

### Remove with Dependencies

```bash
pip uninstall langquality
pip uninstall -r <(pip freeze | grep -E 'spacy|nltk|plotly')
```

## Development Installation

For contributors:

```bash
# Clone repository
git clone https://github.com/langquality/langquality-toolkit.git
cd langquality-toolkit

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install with development dependencies
pip install -e .[dev]

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

## Docker Installation

For containerized deployment:

```bash
# Pull Docker image
docker pull langquality/langquality:latest

# Run analysis
docker run -v $(pwd)/data:/data langquality/langquality \
  analyze -i /data/input.csv -o /data/output --language eng
```

## Next Steps

- [Quick Start Guide](../quickstart.md) - Run your first analysis
- [Configuration Guide](../configuration_guide.md) - Customize settings
- [User Guide](analyzing_data.md) - Learn analysis features
