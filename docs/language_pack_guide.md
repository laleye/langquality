# Language Pack Guide

This guide explains how to create, customize, and use Language Packs in LangQuality.

## What is a Language Pack?

A Language Pack is a collection of configuration files and linguistic resources that enable LangQuality to analyze text in a specific language. Each pack contains:

- **Configuration** - Analysis thresholds and tokenization settings
- **Metadata** - Language information and pack details
- **Resources** - Linguistic data (lexicons, gender terms, etc.)
- **Custom Analyzers** - Optional language-specific analyzers

## Language Pack Structure

```
language_packs/
└── {language_code}/          # ISO 639-3 code (e.g., 'fon', 'eng', 'fra')
    ├── config.yaml            # Main configuration
    ├── metadata.json          # Pack metadata
    ├── README.md              # Documentation
    ├── resources/             # Linguistic resources
    │   ├── lexicon.txt        # Frequency lexicon (optional)
    │   ├── stopwords.txt      # Stop words (optional)
    │   ├── gender_terms.json  # Gendered terms (optional)
    │   ├── professions.json   # Gendered professions (optional)
    │   └── custom/            # Custom resources
    └── analyzers/             # Custom analyzers (optional)
        └── custom_analyzer.py
```

## Creating a New Language Pack

### Step 1: Generate Template

Use the CLI to create a template:

```bash
langquality pack create <language_code>
```

Example:
```bash
langquality pack create swa  # For Swahili
```

This creates a complete template in `language_packs/swa/` with example files.

### Step 2: Edit Metadata

Edit `metadata.json` with your language information:

```json
{
  "version": "1.0.0",
  "author": "Your Name",
  "email": "your.email@example.com",
  "license": "MIT",
  "description": "Language pack for Swahili",
  "created": "2024-03-20",
  "updated": "2024-03-20",
  "contributors": [
    "Your Name"
  ],
  "status": "experimental",
  "coverage": {
    "lexicon_size": 0,
    "domains_covered": [],
    "has_gender_resources": false
  },
  "dependencies": {
    "spacy_model": null,
    "min_langquality_version": "1.0.0"
  },
  "references": []
}
```

**Status values:**
- `experimental` - Early development, may have issues
- `beta` - Functional but needs more testing
- `stable` - Production-ready
- `deprecated` - No longer maintained

### Step 3: Configure Language Settings

Edit `config.yaml`:

```yaml
# Language Pack Configuration
language:
  code: "swa"                    # ISO 639-3 code
  name: "Swahili"
  family: "Niger-Congo"
  script: "Latin"                # Latin, Arabic, Devanagari, etc.
  direction: "ltr"               # ltr (left-to-right) or rtl (right-to-left)

# Tokenization settings
tokenization:
  method: "whitespace"           # spacy, nltk, whitespace, custom
  model: null                    # For spacy: "en_core_web_md"
  custom_rules: []               # Custom tokenization rules

# Analysis thresholds
thresholds:
  structural:
    min_words: 3
    max_words: 20
    min_chars: 10
    max_chars: 200
  
  linguistic:
    max_readability_score: 60.0
    enable_pos_tagging: false    # Requires spaCy model
    enable_dependency_parsing: false
  
  diversity:
    target_ttr: 0.6
    min_unique_words: 100
    check_duplicates: true
  
  domain:
    min_representation: 0.10
    max_representation: 0.30
    balance_threshold: 0.15
  
  gender:
    target_ratio: [0.4, 0.6]
    check_stereotypes: true

# Resource files (all optional)
resources:
  lexicon: "resources/lexicon.txt"
  stopwords: "resources/stopwords.txt"
  gender_terms: "resources/gender_terms.json"
  professions: "resources/professions.json"
  custom: []

# Enabled analyzers
analyzers:
  enabled:
    - structural
    - linguistic
    - diversity
    - domain
  disabled:
    - gender_bias              # Disable if no gender resources

# Custom analyzer plugins
plugins: []
```

### Step 4: Add Linguistic Resources

#### Lexicon (resources/lexicon.txt)

A frequency-ordered word list:

```text
# Format: word frequency
the 1000000
be 800000
to 750000
of 700000
and 650000
...
```

**How to create:**
1. Use a corpus in your target language
2. Count word frequencies
3. Sort by frequency (descending)
4. Save top 5,000-10,000 words

**Tools:**
- Python: `collections.Counter`
- Command line: `cat corpus.txt | tr ' ' '\n' | sort | uniq -c | sort -rn`

#### Stop Words (resources/stopwords.txt)

Common words to filter out:

```text
the
a
an
and
or
but
in
on
at
to
...
```

**How to create:**
1. Identify function words (articles, prepositions, conjunctions)
2. Add high-frequency words with little semantic meaning
3. Typically 100-300 words

**Sources:**
- NLTK stopwords: `nltk.corpus.stopwords.words('language')`
- spaCy: `spacy.lang.xx.stop_words.STOP_WORDS`
- Manual curation from corpus

#### Gender Terms (resources/gender_terms.json)

Gendered words and pronouns:

```json
{
  "male_terms": [
    "he", "him", "his",
    "man", "men",
    "boy", "boys",
    "father", "son", "brother",
    "husband", "boyfriend",
    "king", "prince"
  ],
  "female_terms": [
    "she", "her", "hers",
    "woman", "women",
    "girl", "girls",
    "mother", "daughter", "sister",
    "wife", "girlfriend",
    "queen", "princess"
  ],
  "neutral_terms": [
    "they", "them", "their",
    "person", "people",
    "child", "children",
    "parent", "sibling",
    "spouse", "partner"
  ]
}
```

#### Professions (resources/professions.json)

Gendered profession terms:

```json
{
  "professions": [
    {
      "male": "actor",
      "female": "actress",
      "neutral": "actor"
    },
    {
      "male": "waiter",
      "female": "waitress",
      "neutral": "server"
    },
    {
      "male": "policeman",
      "female": "policewoman",
      "neutral": "police officer"
    }
  ],
  "stereotyped_professions": {
    "male_dominated": [
      "engineer", "programmer", "pilot",
      "mechanic", "construction worker"
    ],
    "female_dominated": [
      "nurse", "teacher", "secretary",
      "receptionist", "caregiver"
    ]
  }
}
```

### Step 5: Write Documentation

Create `README.md` for your pack:

```markdown
# Swahili Language Pack

Language pack for analyzing Swahili text data quality.

## Language Information

- **Language**: Swahili (Kiswahili)
- **ISO 639-3**: swa
- **Family**: Niger-Congo (Bantu)
- **Speakers**: ~100 million
- **Regions**: East Africa (Kenya, Tanzania, Uganda, etc.)

## Features

- ✅ Structural analysis
- ✅ Linguistic analysis (basic)
- ✅ Diversity analysis
- ✅ Domain analysis
- ⚠️ Gender bias analysis (limited resources)

## Resources Included

- **Lexicon**: 5,000 most common words
- **Stop words**: 150 function words
- **Gender terms**: Basic pronouns and kinship terms

## Dependencies

None - uses whitespace tokenization.

## Usage

```bash
langquality analyze -i swahili_data.csv -o results --language swa
```

## Limitations

- No spaCy model available (uses whitespace tokenization)
- Limited gender resources
- Readability scores may not be accurate (designed for English)

## Contributing

To improve this pack:
1. Add more lexicon entries
2. Expand gender term lists
3. Add domain-specific vocabulary
4. Create custom analyzers for Swahili-specific features

## References

- [Swahili Wikipedia](https://sw.wikipedia.org/)
- [Swahili Corpus](https://example.com/swahili-corpus)

## License

MIT License

## Maintainers

- Your Name (@yourusername)
```

### Step 6: Validate the Pack

```bash
langquality pack validate language_packs/swa
```

This checks:
- ✅ Required files exist
- ✅ Configuration is valid YAML
- ✅ Metadata is valid JSON
- ✅ Resource files are properly formatted
- ✅ No syntax errors

### Step 7: Test the Pack

```bash
# Create test data
echo "text,domain
Habari yako?,greeting
Ninakwenda sokoni.,daily_life
Mwalimu anafundisha.,education" > test_swahili.csv

# Run analysis
langquality analyze -i test_swahili.csv -o test_results --language swa

# Check results
open test_results/dashboard.html
```

## Customizing Existing Packs

### Override Configuration

Create a custom config that extends an existing pack:

```yaml
# my_custom_config.yaml
# Extends: eng

thresholds:
  structural:
    min_words: 5      # Override default
    max_words: 12     # Override default
  
  diversity:
    target_ttr: 0.7   # Higher diversity requirement
```

Use it:
```bash
langquality analyze -i data.csv -o results -l eng -c my_custom_config.yaml
```

### Add Custom Resources

Add domain-specific vocabulary:

```bash
# Create custom resource directory
mkdir -p language_packs/eng/resources/custom/

# Add medical terminology
cat > language_packs/eng/resources/custom/medical_terms.txt << EOF
diagnosis
treatment
symptom
medication
EOF
```

Update `config.yaml`:
```yaml
resources:
  custom:
    - "resources/custom/medical_terms.txt"
```

## Tokenization Methods

### Whitespace Tokenization

Simplest method - splits on whitespace:

```yaml
tokenization:
  method: "whitespace"
```

**Pros:**
- No dependencies
- Fast
- Works for most languages

**Cons:**
- Doesn't handle punctuation well
- No linguistic awareness

### spaCy Tokenization

Uses spaCy's linguistic models:

```yaml
tokenization:
  method: "spacy"
  model: "en_core_web_md"
```

**Pros:**
- Linguistically accurate
- Handles punctuation
- Supports POS tagging

**Cons:**
- Requires model download
- Slower
- Not available for all languages

**Available models:**
- English: `en_core_web_md`, `en_core_web_lg`
- French: `fr_core_news_md`, `fr_core_news_lg`
- Spanish: `es_core_news_md`, `es_core_news_lg`
- German: `de_core_news_md`, `de_core_news_lg`
- [More models](https://spacy.io/models)

### NLTK Tokenization

Uses NLTK's tokenizers:

```yaml
tokenization:
  method: "nltk"
```

**Pros:**
- Good for many languages
- Handles punctuation
- Lightweight

**Cons:**
- Requires NLTK data download
- Less accurate than spaCy

### Custom Tokenization

Implement your own tokenizer:

```python
# language_packs/swa/analyzers/swahili_tokenizer.py
from langquality.data.tokenizers import Tokenizer

class SwahiliTokenizer(Tokenizer):
    def tokenize(self, text: str) -> list[str]:
        # Custom tokenization logic
        # Example: Handle Swahili-specific features
        tokens = text.lower().split()
        # Remove punctuation, handle contractions, etc.
        return tokens
```

Register in `config.yaml`:
```yaml
tokenization:
  method: "custom"
  custom_class: "analyzers.swahili_tokenizer.SwahiliTokenizer"
```

## Advanced Features

### Custom Analyzers

Create language-specific analyzers:

```python
# language_packs/swa/analyzers/tone_analyzer.py
from langquality.analyzers.base import Analyzer
from langquality.data.models import Sentence, AnalysisMetrics

class SwahiliToneAnalyzer(Analyzer):
    """Analyzes tone markers in Swahili."""
    
    def get_requirements(self) -> list[str]:
        return []  # No special resources needed
    
    def analyze(self, sentences: list[Sentence]) -> AnalysisMetrics:
        # Analyze tone patterns
        tone_patterns = self._detect_tone_patterns(sentences)
        
        return AnalysisMetrics(
            name="tone_analysis",
            metrics={
                "tone_patterns": tone_patterns,
                "tone_diversity": len(tone_patterns)
            }
        )
    
    def _detect_tone_patterns(self, sentences):
        # Implementation
        pass
```

Register in `config.yaml`:
```yaml
plugins:
  - "analyzers/tone_analyzer.py"
```

### Resource Fallbacks

Handle missing resources gracefully:

```yaml
resources:
  lexicon: "resources/lexicon.txt"
  lexicon_fallback: "resources/basic_lexicon.txt"
  
  gender_terms: "resources/gender_terms.json"
  gender_terms_fallback: null  # Disable gender analysis if missing
```

## Sharing Your Language Pack

### 1. Prepare for Distribution

```bash
# Validate
langquality pack validate language_packs/swa

# Test thoroughly
langquality analyze -i test_data.csv -o test_results -l swa

# Update documentation
# Update metadata.json with final version
```

### 2. Create GitHub Repository

```bash
git init
git add language_packs/swa/
git commit -m "Initial Swahili language pack"
git remote add origin https://github.com/yourusername/langquality-pack-swahili.git
git push -u origin main
```

### 3. Submit to LangQuality

Create a pull request to the main LangQuality repository:

1. Fork [langquality-toolkit](https://github.com/langquality/langquality-toolkit)
2. Add your pack to `src/langquality/language_packs/packs/`
3. Create PR with description:
   - Language information
   - Resource coverage
   - Testing performed
   - Known limitations

### 4. Publish as PyPI Package (Optional)

```bash
# Create setup.py
cat > setup.py << EOF
from setuptools import setup, find_packages

setup(
    name="langquality-pack-swahili",
    version="1.0.0",
    packages=find_packages(),
    install_requires=["langquality>=1.0.0"],
    package_data={
        "": ["*.yaml", "*.json", "*.txt", "*.md"]
    }
)
EOF

# Build and publish
python setup.py sdist bdist_wheel
twine upload dist/*
```

Users can then install:
```bash
pip install langquality-pack-swahili
```

## Language Pack Examples

### Minimal Pack (No Resources)

For languages with no available resources:

```yaml
language:
  code: "xyz"
  name: "Example Language"
  family: "Unknown"
  script: "Latin"
  direction: "ltr"

tokenization:
  method: "whitespace"

thresholds:
  structural:
    min_words: 3
    max_words: 20

resources: {}

analyzers:
  enabled:
    - structural
    - diversity
  disabled:
    - linguistic
    - domain
    - gender_bias
```

### Complete Pack (All Resources)

For well-resourced languages:

```yaml
language:
  code: "eng"
  name: "English"
  family: "Indo-European"
  script: "Latin"
  direction: "ltr"

tokenization:
  method: "spacy"
  model: "en_core_web_md"

thresholds:
  # ... all thresholds configured

resources:
  lexicon: "resources/lexicon.txt"
  stopwords: "resources/stopwords.txt"
  gender_terms: "resources/gender_terms.json"
  professions: "resources/professions.json"
  custom:
    - "resources/custom/domain_keywords.json"

analyzers:
  enabled:
    - structural
    - linguistic
    - diversity
    - domain
    - gender_bias

plugins:
  - "analyzers/sentiment_analyzer.py"
```

## Troubleshooting

### Pack Not Found

```bash
langquality pack list  # Check if pack is installed
langquality pack validate path/to/pack  # Validate pack structure
```

### Invalid Configuration

```bash
# Check YAML syntax
python -c "import yaml; yaml.safe_load(open('config.yaml'))"

# Check JSON syntax
python -c "import json; json.load(open('metadata.json'))"
```

### Resource Loading Errors

```bash
# Check file paths in config.yaml
# Ensure files exist and are readable
ls -la language_packs/xyz/resources/
```

### Tokenization Issues

```bash
# Test tokenizer
python -c "
from langquality.language_packs.manager import LanguagePackManager
pack = LanguagePackManager().load_language_pack('xyz')
print(pack.tokenizer.tokenize('Test sentence'))
"
```

## Best Practices

1. **Start Minimal** - Begin with basic structural analysis, add resources incrementally
2. **Test Thoroughly** - Test with diverse data before sharing
3. **Document Limitations** - Be clear about what works and what doesn't
4. **Version Carefully** - Use semantic versioning, document changes
5. **Cite Sources** - Reference corpora and resources used
6. **Community Feedback** - Share early, get feedback, iterate

## Next Steps

- [Developer Guide](developer_guide/creating_analyzers.md) - Create custom analyzers
- [API Reference](api_reference/) - Detailed API documentation
- [Contributing Guide](../CONTRIBUTING.md) - Contribute to LangQuality
