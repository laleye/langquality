# French Language Pack (fra)

Language pack for French (Français) - A Romance language spoken worldwide.

## Overview

This language pack provides comprehensive support for analyzing French text datasets. It includes full NLP capabilities through spaCy, extensive linguistic resources, and gender bias detection.

## Language Information

- **ISO 639-3 Code**: fra
- **Language Family**: Indo-European > Romance
- **Script**: Latin
- **Direction**: Left-to-right (LTR)
- **Primary Regions**: France, Belgium, Switzerland, Canada, Africa

## Features

### Supported Analyzers

- ✅ **Structural Analysis**: Text length, word count, punctuation, capitalization
- ✅ **Linguistic Analysis**: POS tagging, dependency parsing, readability scores
- ✅ **Diversity Analysis**: Type-token ratio, vocabulary richness, duplicate detection
- ✅ **Domain Analysis**: Domain distribution and balance
- ✅ **Gender Bias Analysis**: Gender representation, stereotypes, profession bias

### Resources Included

1. **Lexicon** (`lexicon.txt`): ~10,000 most common French words
2. **Stopwords** (`stopwords.txt`): ~150 French stopwords
3. **Gender Terms** (`gender_terms.json`): Masculine, feminine, and neutral terms
4. **Professions** (`professions.json`): 30+ professions with gendered forms
5. **Stereotypes** (`gender_stereotypes.json`): Common gender stereotypes in French

## Dependencies

- **spaCy Model**: `fr_core_news_md` (French medium model)
- **Python**: >=3.8
- **LangQuality**: >=1.0.0

## Installation

### Install spaCy Model

```bash
python -m spacy download fr_core_news_md
```

### Use the Language Pack

```python
from langquality.language_packs import LanguagePackManager

manager = LanguagePackManager()
pack = manager.load_language_pack("fra")
print(f"Loaded: {pack.name}")
```

### CLI Usage

```bash
langquality analyze --language fra --input data.csv --output results/
```

## Configuration

The pack uses the following default thresholds:

- **Structural**: 3-25 words, 10-250 characters per sentence
- **Linguistic**: Readability score 0-70
- **Diversity**: Target TTR of 0.65, minimum 150 unique words
- **Domain**: 8-35% representation per domain
- **Gender**: Target ratio 40-60% for balanced representation

These can be customized in `config.yaml`.

## Domains Covered

The pack is optimized for the following domains:
- Health (santé)
- Education (éducation)
- Technology (technologie)
- Business (affaires)
- Culture
- Science
- Politics (politique)
- Sports

## Gender Bias Detection

The French language pack includes comprehensive gender bias detection:

- **Gendered Grammar**: French has grammatical gender for nouns and adjectives
- **Profession Forms**: Tracks masculine/feminine profession forms (e.g., directeur/directrice)
- **Stereotype Detection**: Identifies common gender stereotypes in French culture
- **Balanced Representation**: Monitors gender balance in datasets

## Examples

### Basic Analysis

```python
from langquality import PipelineController
from langquality.language_packs import LanguagePackManager

# Load French pack
manager = LanguagePackManager()
pack = manager.load_language_pack("fra")

# Run analysis
controller = PipelineController(language_pack=pack)
results = controller.run_from_file("french_data.csv")
```

### Custom Configuration

```python
# Modify thresholds
pack.config.thresholds.structural.min_words = 5
pack.config.thresholds.structural.max_words = 30

# Disable specific analyzers
pack.config.analyzers.disabled.append("gender_bias")
```

## Contributing

To improve this language pack:

1. Add more vocabulary to `lexicon.txt`
2. Expand profession list in `professions.json`
3. Add domain-specific terminology
4. Report issues or suggest improvements

See the main CONTRIBUTING.md for guidelines.

## License

MIT License - See LICENSE file in the main repository.

## References

- [spaCy French Models](https://spacy.io/models/fr)
- [French Language Resources](https://github.com/langquality/langquality-toolkit)

## Version History

- **1.0.0** (2024-11-15): Initial release with full NLP support
