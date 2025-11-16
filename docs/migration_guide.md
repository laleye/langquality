# Migration Guide: fongbe-quality to langquality

This guide helps you migrate from `fongbe-quality` (v0.1.0) to `langquality` (v1.0.0).

## Overview

LangQuality is the evolution of the Fongbe Data Quality Pipeline into a generic, multi-language toolkit. The core functionality remains the same, but the architecture has been redesigned to support any low-resource language.

## What's Changed

### Package Name
- **Old**: `fongbe-data-quality` / `fongbe_quality`
- **New**: `langquality`

### Architecture
- **Language Packs**: Language-specific configurations moved to modular packs
- **Plugin System**: Analyzers can be dynamically loaded
- **Generic Loader**: Data loading is now language-agnostic
- **Configurable Tokenization**: Tokenization method specified in language pack

## Migration Steps

### 1. Installation

#### Uninstall Old Package
```bash
pip uninstall fongbe-data-quality
```

#### Install New Package
```bash
pip install langquality
```

#### Verify Installation
```bash
langquality --version
langquality pack list
```

You should see the `fon` (Fongbe) language pack listed.

### 2. Update Imports

#### Python Code

**Before:**
```python
from fongbe_quality.pipeline import PipelineController
from fongbe_quality.data.loader import FongbeDataLoader
from fongbe_quality.analyzers.structural import StructuralAnalyzer
from fongbe_quality.config.loader import load_config
```

**After:**
```python
from langquality.pipeline import PipelineController
from langquality.data.loader import DataLoader
from langquality.analyzers.structural import StructuralAnalyzer
from langquality.config.loader import load_config
from langquality.language_packs import LanguagePackManager
```

#### Automated Migration Script

You can use this script to update imports in your codebase:

```bash
# migration_script.sh
find . -name "*.py" -type f -exec sed -i 's/from fongbe_quality/from langquality/g' {} +
find . -name "*.py" -type f -exec sed -i 's/import fongbe_quality/import langquality/g' {} +
```

### 3. Update CLI Commands

#### Basic Analysis

**Before:**
```bash
fongbe-quality analyze data.csv --output results/
```

**After:**
```bash
langquality analyze --language fon data.csv --output results/
```

#### With Configuration

**Before:**
```bash
fongbe-quality analyze data.csv --config config.yaml
```

**After:**
```bash
langquality analyze --language fon data.csv --config config.yaml
```

#### Backward Compatibility

For a transition period, you can still use the old command:
```bash
fongbe-quality analyze data.csv
```

This will show a deprecation warning and redirect to `langquality --language fon`.

### 4. Update Configuration Files

#### Old Configuration Structure

**Before** (`config.yaml`):
```yaml
analysis:
  structural:
    min_words: 3
    max_words: 20
  linguistic:
    enable_pos_tagging: true
  diversity:
    target_ttr: 0.6

resources:
  lexicon: "resources/french_frequency_lexicon.txt"
  gender_terms: "resources/gender_terms.json"
```

#### New Configuration Structure

**After** - Configuration is now split:

1. **User config** (`config.yaml`) - Analysis settings only:
```yaml
analysis:
  structural:
    min_words: 3
    max_words: 20
  linguistic:
    enable_pos_tagging: true
  diversity:
    target_ttr: 0.6
```

2. **Language pack config** (`language_packs/fon/config.yaml`) - Language-specific settings:
```yaml
language:
  code: "fon"
  name: "Fongbe"
  family: "Niger-Congo"
  script: "Latin"
  direction: "ltr"

tokenization:
  method: "spacy"
  model: "fr_core_news_md"

resources:
  lexicon: "resources/lexicon.txt"
  gender_terms: "resources/gender_terms.json"
  professions: "resources/professions.json"
```

### 5. Update Python Code

#### Data Loading

**Before:**
```python
from fongbe_quality.data.loader import FongbeDataLoader

loader = FongbeDataLoader()
sentences = loader.load_from_csv("data.csv", text_column="text")
```

**After:**
```python
from langquality.data.loader import DataLoader
from langquality.language_packs import LanguagePackManager

pack_manager = LanguagePackManager()
language_pack = pack_manager.load_language_pack("fon")

loader = DataLoader(language_pack)
sentences = loader.load_from_csv("data.csv", text_column="text")
```

#### Pipeline Execution

**Before:**
```python
from fongbe_quality.pipeline import PipelineController
from fongbe_quality.config.loader import load_config

config = load_config("config.yaml")
controller = PipelineController(config)
results = controller.run(sentences)
```

**After:**
```python
from langquality.pipeline import PipelineController
from langquality.config.loader import load_config
from langquality.language_packs import LanguagePackManager

config = load_config("config.yaml")
pack_manager = LanguagePackManager()
language_pack = pack_manager.load_language_pack("fon")

controller = PipelineController(config, language_pack)
results = controller.run(sentences)
```

#### Custom Analyzers

**Before:**
```python
from fongbe_quality.analyzers.base import Analyzer

class MyAnalyzer(Analyzer):
    def __init__(self, config):
        super().__init__(config)
    
    def analyze(self, sentences):
        # Analysis logic
        pass
```

**After:**
```python
from langquality.analyzers.base import Analyzer

class MyAnalyzer(Analyzer):
    def __init__(self, config, language_pack=None):
        super().__init__(config, language_pack)
    
    def get_requirements(self):
        """Declare required resources."""
        return ["lexicon"]  # Optional
    
    def analyze(self, sentences):
        # Analysis logic
        # Access language pack: self.language_pack
        pass
```

### 6. Migrate Custom Resources

If you have custom resources for Fongbe:

#### Option 1: Add to Existing Fongbe Pack

1. Locate the Fongbe language pack:
```bash
python -c "from langquality.language_packs import LanguagePackManager; print(LanguagePackManager().get_pack_path('fon'))"
```

2. Add your resources to `resources/custom/`:
```
language_packs/fon/
└── resources/
    └── custom/
        ├── my_lexicon.txt
        └── my_terms.json
```

3. Update `config.yaml`:
```yaml
resources:
  custom:
    - "resources/custom/my_lexicon.txt"
    - "resources/custom/my_terms.json"
```

#### Option 2: Create Custom Language Pack

For heavily customized Fongbe configurations:

```bash
langquality pack create fon-custom
```

Then copy and modify the Fongbe pack resources.

### 7. Update Tests

#### Test Imports

**Before:**
```python
from fongbe_quality.analyzers.structural import StructuralAnalyzer
from fongbe_quality.data.models import Sentence
```

**After:**
```python
from langquality.analyzers.structural import StructuralAnalyzer
from langquality.data.models import Sentence
from langquality.language_packs import LanguagePackManager
```

#### Test Fixtures

**Before:**
```python
@pytest.fixture
def analyzer():
    config = AnalysisConfig()
    return StructuralAnalyzer(config)
```

**After:**
```python
@pytest.fixture
def language_pack():
    pack_manager = LanguagePackManager()
    return pack_manager.load_language_pack("fon")

@pytest.fixture
def analyzer(language_pack):
    config = AnalysisConfig()
    return StructuralAnalyzer(config, language_pack)
```

### 8. Update CI/CD Pipelines

#### GitHub Actions

**Before:**
```yaml
- name: Install dependencies
  run: |
    pip install fongbe-data-quality
    
- name: Run analysis
  run: |
    fongbe-quality analyze data.csv
```

**After:**
```yaml
- name: Install dependencies
  run: |
    pip install langquality
    python -m spacy download fr_core_news_md
    
- name: Run analysis
  run: |
    langquality analyze --language fon data.csv
```

### 9. Update Documentation

Update any documentation that references:
- Package name: `fongbe-data-quality` → `langquality`
- Module paths: `fongbe_quality.*` → `langquality.*`
- CLI commands: `fongbe-quality` → `langquality --language fon`
- Installation instructions
- Code examples

## Common Issues and Solutions

### Issue 1: Import Errors

**Error:**
```
ModuleNotFoundError: No module named 'fongbe_quality'
```

**Solution:**
```bash
pip uninstall fongbe-data-quality
pip install langquality
# Update all imports in your code
```

### Issue 2: Missing Language Pack

**Error:**
```
LanguagePackError: Language pack 'fon' not found
```

**Solution:**
```bash
# Verify installation
langquality pack list

# Reinstall if needed
pip install --force-reinstall langquality
```

### Issue 3: Tokenization Errors

**Error:**
```
OSError: [E050] Can't find model 'fr_core_news_md'
```

**Solution:**
```bash
python -m spacy download fr_core_news_md
```

### Issue 4: Configuration Not Found

**Error:**
```
ConfigurationError: Could not load language pack configuration
```

**Solution:**
Ensure your language pack has a valid `config.yaml`:
```bash
langquality pack validate language_packs/fon/
```

### Issue 5: Resource Files Not Loading

**Error:**
```
ResourceNotFoundError: Required resource 'lexicon' not found
```

**Solution:**
Check that resources are in the correct location:
```
language_packs/fon/
└── resources/
    └── lexicon.txt  # Must exist
```

Or disable analyzers that require missing resources in `config.yaml`:
```yaml
analyzers:
  enabled:
    - structural
    - diversity
  disabled:
    - linguistic  # Requires lexicon
```

## Backward Compatibility

### Deprecation Timeline

- **v1.0.0 - v1.2.0**: Deprecation warnings for old imports and CLI
- **v1.3.0**: Remove backward compatibility aliases
- **v2.0.0**: Complete removal of legacy code

### Using Legacy Code

If you need to maintain compatibility with both versions:

```python
try:
    from langquality.pipeline import PipelineController
    from langquality.language_packs import LanguagePackManager
    LANGQUALITY_VERSION = 1
except ImportError:
    from fongbe_quality.pipeline import PipelineController
    LANGQUALITY_VERSION = 0

if LANGQUALITY_VERSION == 1:
    pack_manager = LanguagePackManager()
    language_pack = pack_manager.load_language_pack("fon")
    controller = PipelineController(config, language_pack)
else:
    controller = PipelineController(config)
```

## Benefits of Migration

After migrating to LangQuality, you'll benefit from:

1. **Multi-language support**: Easily analyze data in multiple languages
2. **Extensibility**: Add custom analyzers without modifying core code
3. **Better documentation**: Comprehensive guides and API docs
4. **Active community**: Contribute and get support from the community
5. **Regular updates**: Ongoing development and improvements
6. **Better testing**: More robust with higher test coverage
7. **Modern architecture**: Cleaner, more maintainable codebase

## Getting Help

If you encounter issues during migration:

1. **Check the documentation**: [https://langquality.readthedocs.io](https://langquality.readthedocs.io)
2. **Search existing issues**: [GitHub Issues](https://github.com/langquality/langquality-toolkit/issues)
3. **Ask in discussions**: [GitHub Discussions](https://github.com/langquality/langquality-toolkit/discussions)
4. **Report bugs**: Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md)

## Migration Checklist

Use this checklist to track your migration progress:

- [ ] Uninstall `fongbe-data-quality`
- [ ] Install `langquality`
- [ ] Verify Fongbe language pack is available
- [ ] Update all imports in Python code
- [ ] Update CLI commands in scripts
- [ ] Migrate configuration files
- [ ] Update custom analyzers (if any)
- [ ] Migrate custom resources
- [ ] Update tests
- [ ] Update CI/CD pipelines
- [ ] Update documentation
- [ ] Test thoroughly with your data
- [ ] Deploy to production

## Feedback

We'd love to hear about your migration experience! Please share:
- What went well
- What was challenging
- Suggestions for improving this guide

Open a discussion: [Migration Feedback](https://github.com/langquality/langquality-toolkit/discussions)

---

**Last Updated**: 2024  
**Applies to**: langquality v1.0.0  
**Migrating from**: fongbe-quality v0.1.0
