# English Language Pack (eng)

Language pack for English - A Germanic language spoken worldwide.

## Overview

This language pack provides comprehensive support for analyzing English text datasets. It includes full NLP capabilities through spaCy, extensive linguistic resources, and gender bias detection.

## Language Information

- **ISO 639-3 Code**: eng
- **Language Family**: Indo-European > Germanic
- **Script**: Latin
- **Direction**: Left-to-right (LTR)
- **Primary Regions**: United States, United Kingdom, Canada, Australia, New Zealand, worldwide

## Features

### Supported Analyzers

- ✅ **Structural Analysis**: Text length, word count, punctuation, capitalization
- ✅ **Linguistic Analysis**: POS tagging, dependency parsing, readability scores
- ✅ **Diversity Analysis**: Type-token ratio, vocabulary richness, duplicate detection
- ✅ **Domain Analysis**: Domain distribution and balance
- ✅ **Gender Bias Analysis**: Gender representation, stereotypes, profession bias

### Resources Included

1. **Lexicon** (`lexicon.txt`): ~15,000 most common English words
2. **Stopwords** (`stopwords.txt`): ~180 English stopwords
3. **Gender Terms** (`gender_terms.json`): Masculine, feminine, and neutral terms (including non-binary pronouns)
4. **Professions** (`professions.json`): 45+ professions with gendered forms
5. **Stereotypes** (`gender_stereotypes.json`): Common gender stereotypes in English

## Dependencies

- **spaCy Model**: `en_core_web_md` (English medium model)
- **Python**: >=3.8
- **LangQuality**: >=1.0.0

## Installation

### Install spaCy Model

```bash
python -m spacy download en_core_web_md
```

### Use the Language Pack

```python
from langquality.language_packs import LanguagePackManager

manager = LanguagePackManager()
pack = manager.load_language_pack("eng")
print(f"Loaded: {pack.name}")
```

### CLI Usage

```bash
langquality analyze --language eng --input data.csv --output results/
```

## Configuration

The pack uses the following default thresholds:

- **Structural**: 3-30 words, 10-300 characters per sentence
- **Linguistic**: Readability score 0-80
- **Diversity**: Target TTR of 0.70, minimum 200 unique words
- **Domain**: 5-40% representation per domain
- **Gender**: Target ratio 40-60% for balanced representation

These can be customized in `config.yaml`.

## Domains Covered

The pack is optimized for the following domains:
- Health
- Education
- Technology
- Business
- Culture
- Science
- Politics
- Sports
- Entertainment
- Finance

## Gender Bias Detection

The English language pack includes comprehensive gender bias detection:

- **Grammatical Gender**: English has minimal grammatical gender but uses gendered pronouns
- **Profession Forms**: Tracks gendered profession terms (e.g., actor/actress, waiter/waitress)
- **Stereotype Detection**: Identifies common gender stereotypes in English-speaking cultures
- **Balanced Representation**: Monitors gender balance in datasets
- **Non-Binary Support**: Includes neutral pronouns (they/them, ze/hir, xe/xem)

### Common Stereotypes Detected

- **Domestic roles** associated with women (housework, childcare)
- **Professional roles** associated with men (leadership, technical fields)
- **Emotional traits** associated with women (sensitive, caring)
- **Physical traits** associated with men (strong, aggressive)
- **Appearance focus** for women vs. **competence focus** for men

## Examples

### Basic Analysis

```python
from langquality import PipelineController
from langquality.language_packs import LanguagePackManager

# Load English pack
manager = LanguagePackManager()
pack = manager.load_language_pack("eng")

# Run analysis
controller = PipelineController(language_pack=pack)
results = controller.run_from_file("english_data.csv")
```

### Custom Configuration

```python
# Modify thresholds
pack.config.thresholds.structural.min_words = 5
pack.config.thresholds.structural.max_words = 35

# Disable specific analyzers
pack.config.analyzers.disabled.append("gender_bias")
```

### Gender-Neutral Language Analysis

```python
# Check for gender-neutral language usage
results = controller.run_from_file("data.csv")
gender_metrics = results.get_analyzer_results("gender_bias")

# Analyze pronoun usage
pronoun_distribution = gender_metrics.pronoun_distribution
print(f"They/them usage: {pronoun_distribution.get('neutral', 0)}%")
```

## Best Practices

### For Dataset Creation

1. **Use gender-neutral terms** when possible (e.g., "firefighter" instead of "fireman")
2. **Balance gender representation** across all domains
3. **Avoid stereotypical associations** (e.g., nurses are always women, engineers are always men)
4. **Include diverse perspectives** in your dataset

### For Analysis

1. **Review stereotype warnings** carefully
2. **Check profession bias** metrics
3. **Monitor pronoun distribution** for balance
4. **Consider context** when interpreting results

## Contributing

To improve this language pack:

1. Add more vocabulary to `lexicon.txt`
2. Expand profession list in `professions.json`
3. Add domain-specific terminology
4. Update stereotype patterns based on research
5. Report issues or suggest improvements

See the main CONTRIBUTING.md for guidelines.

## License

MIT License - See LICENSE file in the main repository.

## References

- [spaCy English Models](https://spacy.io/models/en)
- [Gender-Neutral Language Guidelines](https://www.un.org/en/gender-inclusive-language/)
- [English Language Resources](https://github.com/langquality/langquality-toolkit)

## Version History

- **1.0.0** (2024-11-15): Initial release with full NLP support and comprehensive gender bias detection
