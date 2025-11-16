# Language Pack System

This module implements the Language Pack system for LangQuality, enabling language-agnostic data quality analysis.

## Overview

The Language Pack system allows users to:
- Configure language-specific analysis parameters
- Provide language-specific resources (lexicons, stopwords, etc.)
- Create and share language packs for different languages
- Validate language pack structures

## Components

### 1. Data Models (`models.py`)

Core data structures for Language Packs:

- **LanguagePack**: Complete language pack with configuration, metadata, and resources
- **LanguageConfig**: Language-specific configuration (tokenization, thresholds, analyzers)
- **PackMetadata**: Pack metadata (version, author, license, etc.)
- **ThresholdConfig**: Analysis thresholds for all analyzers
- **TokenizationConfig**: Tokenization settings
- **ResourceConfig**: Resource file paths

### 2. Language Pack Manager (`manager.py`)

Manages loading and caching of language packs:

```python
from langquality.language_packs import LanguagePackManager

manager = LanguagePackManager()

# List available packs
packs = manager.list_available_packs()

# Load a pack
pack = manager.load_language_pack('fon')

# Get pack info without loading
info = manager.get_pack_info('fon')

# Validate a pack
is_valid, errors, warnings = manager.validate_pack(pack_path)
```

### 3. Validation (`validation.py`)

Validates language pack structure and content:

```python
from langquality.language_packs import LanguagePackValidator

validator = LanguagePackValidator()

# Validate complete pack
is_valid, errors, warnings = validator.validate_complete_pack(pack_path)

# Validate config only
is_valid, errors = validator.validate_config_yaml(config_data)

# Validate metadata only
is_valid, errors = validator.validate_metadata_json(metadata)
```

### 4. Template Generator (`templates.py`)

Creates new language pack templates:

```python
from langquality.language_packs import LanguagePackTemplate
from pathlib import Path

# Create minimal template
template_path = LanguagePackTemplate.create_template(
    language_code='eng',
    language_name='English',
    output_dir=Path('./packs'),
    author='Your Name',
    email='your@email.com',
    minimal=True
)

# Create complete template with example resources
template_path = LanguagePackTemplate.create_template(
    language_code='eng',
    language_name='English',
    output_dir=Path('./packs'),
    author='Your Name',
    email='your@email.com',
    minimal=False
)
```

## Language Pack Structure

```
language_code/
├── config.yaml          # Main configuration
├── metadata.json        # Pack metadata
├── resources/           # Language-specific resources (optional)
│   ├── lexicon.txt
│   ├── stopwords.txt
│   ├── gender_terms.json
│   ├── professions.json
│   └── custom/
└── README.md           # Pack documentation
```

## Example Packs

The module includes example packs for reference:

- **min**: Minimal example with only required fields
- **cmp**: Complete example with all features
- **_template**: Template for creating new packs

## Creating a New Language Pack

1. Use the template generator:
```python
from langquality.language_packs import LanguagePackTemplate
from pathlib import Path

LanguagePackTemplate.create_template(
    'your_code', 'Your Language', Path('./output')
)
```

2. Edit the generated files:
   - Update `config.yaml` with language-specific settings
   - Update `metadata.json` with pack information
   - Add resources to `resources/` directory

3. Validate the pack:
```python
from langquality.language_packs import LanguagePackManager

manager = LanguagePackManager()
is_valid, errors, warnings = manager.validate_pack(pack_path)
```

4. Test loading:
```python
pack = manager.load_language_pack('your_code')
```

## Configuration Reference

### config.yaml

```yaml
language:
  code: "xxx"              # ISO 639-3 code (required)
  name: "Language Name"    # Full name (required)
  family: "Family"         # Language family (optional)
  script: "Latin"          # Writing script (optional)
  direction: "ltr"         # Text direction (optional)

tokenization:
  method: "whitespace"     # spacy, nltk, whitespace, custom
  model: null              # Model name for spacy/nltk
  custom_rules: []         # Custom rules

thresholds:                # All optional
  structural:
    min_words: 3
    max_words: 20
  linguistic:
    max_readability_score: 60.0
  diversity:
    target_ttr: 0.6
  domain:
    min_representation: 0.10
  gender:
    target_ratio: [0.4, 0.6]

analyzers:
  enabled: [structural, linguistic, diversity, domain]
  disabled: []

resources:                 # All optional
  lexicon: "lexicon.txt"
  stopwords: "stopwords.txt"
  gender_terms: "gender_terms.json"
  professions: "professions.json"

plugins: []                # Custom analyzer plugins
```

### metadata.json

```json
{
  "version": "1.0.0",
  "author": "Your Name",
  "email": "your@email.com",
  "license": "MIT",
  "description": "Pack description",
  "created": "2024-01-01",
  "updated": "2024-01-01",
  "contributors": ["Name 1", "Name 2"],
  "status": "stable",
  "coverage": {
    "lexicon_size": 1000,
    "domains_covered": ["health", "education"],
    "has_gender_resources": true
  },
  "dependencies": {
    "min_langquality_version": "1.0.0"
  },
  "references": []
}
```

## Resource Files

### lexicon.txt
One word per line, typically ordered by frequency:
```
word1
word2
word3
```

### stopwords.txt
Common stopwords, one per line:
```
the
a
an
```

### gender_terms.json
Gender-related terms:
```json
{
  "masculine": ["he", "him"],
  "feminine": ["she", "her"],
  "neutral": ["they", "them"]
}
```

### professions.json
Gendered professions:
```json
{
  "professions": [
    {
      "neutral": "teacher",
      "masculine": "male teacher",
      "feminine": "female teacher"
    }
  ]
}
```

## Testing

Run tests to verify the implementation:

```bash
python3 -c "
import sys
sys.path.insert(0, 'src')
from langquality.language_packs import LanguagePackManager

manager = LanguagePackManager()
print('Available packs:', manager.list_available_packs())

pack = manager.load_language_pack('cmp')
print(f'Loaded: {pack.name}')
print(f'Resources: {pack.list_resources()}')
"
```

## Requirements

The Language Pack system requires:
- Python 3.8+
- PyYAML for config parsing
- Standard library modules (json, pathlib, logging)

## Future Enhancements

- Remote pack installation from URLs
- Pack versioning and updates
- Pack dependencies and inheritance
- Automatic resource generation tools
- Community pack registry
