# Language Pack Template

This is a comprehensive template for creating new Language Packs for LangQuality. Use this as a starting point to add support for your language.

## Quick Start

### 1. Copy This Template

```bash
# Replace 'xxx' with your language's ISO 639-3 code
cp -r _template/ xxx/
cd xxx/
```

Find your language's ISO 639-3 code at: https://iso639-3.sil.org/

### 2. Edit Configuration Files

#### `config.yaml` (Required)

Update the following sections:

**Language Information** (Required):
- `language.code`: Your language's ISO 639-3 code (e.g., "eng", "fra", "swa")
- `language.name`: Full language name in English (e.g., "English", "French", "Swahili")
- `language.script`: Writing system (e.g., "Latin", "Arabic", "Cyrillic", "Devanagari")
- `language.direction`: Text direction ("ltr" or "rtl")

**Tokenization** (Required):
- Choose a tokenization method:
  - `"spacy"`: Best for languages with spaCy models (requires installation)
  - `"nltk"`: Good for languages with NLTK support
  - `"whitespace"`: Simple space-based splitting (works for most languages)
  - `"custom"`: Implement your own tokenizer (advanced)

**Thresholds** (Optional):
- Adjust based on your language's characteristics
- For agglutinative languages: increase `max_words` and `max_chars`
- For isolating languages: may need lower thresholds
- For tonal languages: consider linguistic analysis settings

**Analyzers** (Optional):
- Enable analyzers based on available resources
- Disable `gender_bias` if you don't have gender resources

#### `metadata.json` (Required)

Update:
- `author`, `email`: Your contact information
- `description`: Brief description of your language pack
- `created`, `updated`: Current date
- `status`: Start with "experimental", move to "beta" then "stable"
- `coverage`: Update as you add resources
- `dependencies`: List required spaCy models or NLTK data

### 3. Add Resources (Optional but Recommended)

Create a `resources/` directory and add linguistic resources:

#### Minimal Pack (No Resources)
You can create a minimal pack with just `config.yaml` and `metadata.json`. The structural and basic diversity analyzers will still work.

#### Basic Pack (Recommended)
Add these resources for better analysis:
- `lexicon.txt`: Common words in your language
- `stopwords.txt`: Function words and common stopwords

#### Full Pack (Best)
Add all resources for comprehensive analysis:
- `lexicon.txt`: Frequency lexicon (5,000-15,000 words)
- `stopwords.txt`: Stopwords (100-200 words)
- `gender_terms.json`: Gender-related terms (if applicable)
- `professions.json`: Gendered professions (if applicable)
- `gender_stereotypes.json`: Common stereotypes (if applicable)

## Resource File Formats

### lexicon.txt

One word per line, ideally sorted by frequency (most common first):

```
the
be
to
of
and
...
```

**How to create**:
- Use a frequency dictionary for your language
- Extract from a large corpus
- Start with 1,000-5,000 most common words
- Sources: Wikipedia dumps, news corpora, linguistic databases

### stopwords.txt

Common function words that don't carry much meaning:

```
the
a
an
is
are
...
```

**How to create**:
- Include articles, pronouns, prepositions, conjunctions
- Include common auxiliary verbs
- Typically 100-200 words
- Sources: NLTK stopword lists, linguistic resources

### gender_terms.json

Gender-related terms in your language:

```json
{
  "masculine": {
    "pronouns": ["he", "him", "his"],
    "titles": ["mr", "sir"],
    "terms": ["man", "boy", "father"]
  },
  "feminine": {
    "pronouns": ["she", "her", "hers"],
    "titles": ["mrs", "ms", "miss"],
    "terms": ["woman", "girl", "mother"]
  },
  "neutral": {
    "pronouns": ["they", "them", "their"],
    "terms": ["person", "child", "parent"]
  }
}
```

**Notes**:
- Only needed if your language has grammatical or social gender
- Include all pronoun forms
- Add common gendered terms
- Include neutral alternatives if available

### professions.json

Professions with gendered forms:

```json
{
  "professions": [
    {
      "neutral": "teacher",
      "masculine": "male teacher",
      "feminine": "female teacher"
    },
    {
      "neutral": "doctor",
      "masculine": "doctor",
      "feminine": "doctor"
    }
  ]
}
```

**Notes**:
- Include 20-50 common professions
- Use neutral form as base when possible
- Include both gendered and gender-neutral professions
- Helps detect profession bias in datasets

### gender_stereotypes.json

Common gender stereotypes in your language/culture:

```json
{
  "stereotypes": [
    {
      "category": "domestic",
      "gender": "feminine",
      "terms": ["cooking", "cleaning", "childcare"]
    },
    {
      "category": "professional",
      "gender": "masculine",
      "terms": ["leadership", "business", "career"]
    }
  ],
  "context_patterns": [
    {
      "pattern": "working mother",
      "category": "professional",
      "gender": "feminine",
      "note": "Implies conflict with domestic role"
    }
  ]
}
```

**Notes**:
- Document stereotypes specific to your culture
- Include both term-based and pattern-based stereotypes
- Categories: domestic, professional, emotional, physical, appearance, technical, care, leadership
- Helps identify biased language in datasets

## Testing Your Language Pack

### Validation

```bash
# Validate your pack structure and configuration
langquality pack validate /path/to/your/pack
```

### Loading Test

```python
from langquality.language_packs import LanguagePackManager

# Load your pack
manager = LanguagePackManager()
pack = manager.load_language_pack("xxx")  # Your language code

# Check what loaded
print(f"Loaded: {pack.name}")
print(f"Tokenization: {pack.config.tokenization.method}")
print(f"Enabled analyzers: {pack.config.analyzers.enabled}")
print(f"Available resources: {list(pack.resources.keys())}")
```

### Analysis Test

```python
from langquality import PipelineController
from langquality.language_packs import LanguagePackManager

# Load your pack
manager = LanguagePackManager()
pack = manager.load_language_pack("xxx")

# Create test data
test_sentences = [
    {"text": "Test sentence 1", "domain": "test"},
    {"text": "Test sentence 2", "domain": "test"},
]

# Run analysis
controller = PipelineController(language_pack=pack)
results = controller.run(test_sentences)

# Check results
print(f"Analyzed {len(test_sentences)} sentences")
print(f"Results: {results}")
```

## Language-Specific Considerations

### Agglutinative Languages (Turkish, Finnish, Hungarian, etc.)
- Increase `max_words` and `max_chars` thresholds
- Words can be very long due to affixation
- Consider custom tokenization rules

### Isolating Languages (Chinese, Vietnamese, Thai, etc.)
- May need lower `min_words` threshold
- Consider character-based metrics in addition to word-based
- Tokenization is crucial - use appropriate tools

### Tonal Languages (Mandarin, Thai, Vietnamese, etc.)
- Ensure lexicon includes tone markers if written
- Consider phonetic resources if available

### Right-to-Left Languages (Arabic, Hebrew, Urdu, etc.)
- Set `direction: "rtl"` in config
- Ensure resources use correct script
- Test with RTL text editors

### Languages with Grammatical Gender (French, Spanish, German, etc.)
- Gender resources are highly recommended
- Include all gender agreement forms
- Document gender-neutral alternatives if emerging

### Low-Resource Languages
- Start with minimal pack (no resources)
- Structural analysis will still work
- Add resources incrementally as available
- Consider using related language as bridge (like Fongbe uses French)

## Best Practices

### Resource Quality
1. **Lexicon**: Use frequency-based word lists from reliable corpora
2. **Stopwords**: Include only true function words
3. **Gender Terms**: Be comprehensive and culturally appropriate
4. **Professions**: Include diverse range of occupations
5. **Stereotypes**: Document objectively, include cultural context

### Configuration
1. **Thresholds**: Test with real data and adjust
2. **Tokenization**: Choose the best available method for your language
3. **Analyzers**: Only enable what you can support with resources
4. **Documentation**: Explain language-specific decisions

### Testing
1. **Validate**: Always run validation before sharing
2. **Test Data**: Use diverse, real-world examples
3. **Edge Cases**: Test with unusual but valid sentences
4. **Performance**: Check with large datasets (1000+ sentences)

### Documentation
1. **README**: Explain language-specific features and limitations
2. **Comments**: Add comments in config.yaml for clarity
3. **References**: Cite sources for linguistic resources
4. **Examples**: Provide usage examples

## Contributing Your Language Pack

Once your language pack is ready and tested:

1. **Validate**: Ensure it passes validation
2. **Document**: Complete README with language-specific information
3. **Test**: Run full test suite
4. **Submit**: Create a pull request to the main repository

See the main CONTRIBUTING.md for detailed guidelines.

### Contribution Checklist

- [ ] ISO 639-3 code is correct
- [ ] `config.yaml` is complete and valid
- [ ] `metadata.json` is complete
- [ ] README.md documents language-specific features
- [ ] Resources are properly formatted (if included)
- [ ] Pack passes validation: `langquality pack validate`
- [ ] Tested with sample data
- [ ] All files use UTF-8 encoding
- [ ] License is compatible (MIT recommended)

## Getting Help

- **Documentation**: https://langquality.readthedocs.io/
- **GitHub Issues**: https://github.com/langquality/langquality-toolkit/issues
- **Discussions**: https://github.com/langquality/langquality-toolkit/discussions
- **Examples**: See `fon/`, `fra/`, and `eng/` packs for reference

## Resources for Language Pack Creation

### Finding ISO 639-3 Codes
- https://iso639-3.sil.org/

### Linguistic Resources
- **Universal Dependencies**: https://universaldependencies.org/
- **WALS (World Atlas of Language Structures)**: https://wals.info/
- **Ethnologue**: https://www.ethnologue.com/
- **Glottolog**: https://glottolog.org/

### Corpus Resources
- **Wikipedia Dumps**: https://dumps.wikimedia.org/
- **Common Crawl**: https://commoncrawl.org/
- **OPUS (parallel corpora)**: https://opus.nlpl.eu/

### NLP Tools
- **spaCy Models**: https://spacy.io/models
- **NLTK Data**: https://www.nltk.org/data.html
- **Stanza**: https://stanfordnlp.github.io/stanza/

## License

This template is released under the MIT License. Your language pack should use a compatible open-source license.

## Version History

- **1.0.0** (2024-11-15): Comprehensive template with detailed documentation
