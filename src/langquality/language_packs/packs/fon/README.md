# Fongbe Language Pack

## Overview

This language pack provides resources and configuration for analyzing data quality in Fongbe (ISO 639-3: `fon`), a Gbe language spoken primarily in Benin and Togo.

**Language Family**: Niger-Congo > Atlantic-Congo > Volta-Congo > Kwa > Gbe  
**Speakers**: ~2.5 million  
**Region**: Benin (primary), Togo  
**Script**: Latin alphabet

## About Fongbe

Fongbe is a low-resource language with limited NLP tools and resources. This language pack uses French as a bridge language for linguistic analysis, as many Fongbe speakers are bilingual and datasets often contain French-Fongbe parallel text for ASR and translation applications.

## Resources Included

### 1. Lexicon (`resources/lexicon.txt`)
- **Size**: ~5,000 words
- **Source**: French frequency lexicon (used as bridge language)
- **Format**: Word frequency pairs
- **Usage**: Vocabulary coverage analysis, readability assessment

### 2. ASR Reference Vocabulary (`resources/asr_reference_vocabulary.txt`)
- **Size**: ~500 essential words
- **Purpose**: Core vocabulary for Automatic Speech Recognition systems
- **Categories**: Numbers, common phrases, domain-specific terms
- **Usage**: ASR dataset quality validation

### 3. Gender Terms (`resources/gender_terms.json`)
- **Content**: Masculine and feminine pronouns, articles, titles
- **Language**: French (bridge language)
- **Usage**: Gender representation analysis in bilingual datasets

### 4. Gendered Professions (`resources/professions.json`)
- **Content**: 15+ professions with masculine/feminine forms
- **Usage**: Profession-based gender bias detection

### 5. Gender Stereotypes (`resources/gender_stereotypes.json`)
- **Content**: 6 stereotype categories with regex patterns
- **Categories**:
  - Profession associations (masculine/feminine)
  - Domestic role associations
  - Leadership associations
  - Emotional trait associations
  - Physical strength associations
- **Usage**: Stereotype detection in training data

## Configuration

### Tokenization
- **Method**: SpaCy with French model (`fr_core_news_md`)
- **Rationale**: Fongbe lacks dedicated NLP models; French serves as bridge language
- **Fallback**: Whitespace tokenization

### Analysis Thresholds

#### Structural Analysis
- Sentence length: 3-20 words
- Character count: 10-200 characters
- Checks: Punctuation, capitalization

#### Linguistic Analysis
- Readability score: 0-60 (Flesch-Kincaid)
- POS tagging: Enabled
- Dependency parsing: Disabled (limited accuracy for Fongbe)

#### Diversity Analysis
- Target Type-Token Ratio (TTR): 0.6
- Minimum unique words: 100
- Duplicate detection: Enabled (95% threshold)

#### Domain Balance
- Minimum representation: 10% per domain
- Maximum representation: 30% per domain
- Balance threshold: 15%

#### Gender Bias
- Target gender ratio: 40-60%
- Stereotype detection: Enabled
- Profession bias checking: Enabled

### Supported Domains

1. **Health** (Santé)
2. **Education** (Éducation)
3. **Agriculture**
4. **Commerce**
5. **Family** (Famille)
6. **Public Services** (Services publics)

## Usage

### Basic Usage

```bash
# Analyze Fongbe dataset
langquality analyze --language fon --input data/fongbe_sentences.csv

# List available analyzers for Fongbe
langquality pack info fon
```

### Python API

```python
from langquality.language_packs import LanguagePackManager
from langquality.pipeline import PipelineController

# Load Fongbe language pack
manager = LanguagePackManager()
fon_pack = manager.load_language_pack("fon")

# Initialize pipeline
pipeline = PipelineController(language_pack=fon_pack)

# Run analysis
results = pipeline.run(sentences)
```

## Limitations

1. **Bridge Language Dependency**: Relies on French NLP tools, which may not capture Fongbe-specific linguistic features
2. **Limited Morphological Analysis**: Fongbe has different morphology than French
3. **Tonal Information**: Does not analyze tonal patterns (important in Fongbe)
4. **Code-Switching**: May not handle French-Fongbe code-switching optimally

## Extending This Pack

### Adding Fongbe-Specific Resources

To improve this pack with native Fongbe resources:

1. **Fongbe Lexicon**: Replace French lexicon with Fongbe word frequency list
2. **Tone Markers**: Add tonal pattern validation
3. **Morphological Rules**: Add Fongbe-specific morphology checks
4. **Native Tokenizer**: Implement Fongbe-aware tokenization

### Custom Analyzers

Create custom analyzers for Fongbe-specific features:

```python
# Example: Tone pattern analyzer
from langquality.analyzers import Analyzer

class FongbeToneAnalyzer(Analyzer):
    def analyze(self, sentences):
        # Analyze tonal patterns
        pass
```

Place custom analyzers in `analyzers/` directory.

## Contributing

Contributions to improve this language pack are welcome! Areas for improvement:

- Native Fongbe linguistic resources
- Fongbe-specific NLP tools integration
- Expanded domain coverage
- Cultural context validation
- Tonal analysis capabilities

## References

1. Fongbe Language Documentation
2. French-Fongbe Parallel Corpora
3. Low-Resource Language ASR Best Practices
4. Niger-Congo Language Family Studies

## License

MIT License - See main project LICENSE file

## Maintainers

- Original Fongbe Data Quality Project Team

## Version History

- **1.0.0** (2024-11-15): Initial release with migrated resources from fongbe-data-quality project
  - French lexicon (5,000 words)
  - ASR reference vocabulary (500 words)
  - Gender analysis resources
  - Stereotype detection patterns
  - Domain-specific configurations

## Support

For questions or issues specific to this language pack:
- Open an issue on GitHub
- Tag with `language-pack:fon`
- Consult the main LangQuality documentation
