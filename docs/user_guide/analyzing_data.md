# Analyzing Data with LangQuality

This guide covers how to analyze text data quality using LangQuality's comprehensive analysis features.

## Overview

LangQuality analyzes text data across five key dimensions:

1. **Structural Analysis** - Sentence length, character counts, formatting
2. **Linguistic Analysis** - Readability, complexity, vocabulary
3. **Diversity Analysis** - Vocabulary richness, duplicates, n-grams
4. **Domain Analysis** - Thematic distribution and balance
5. **Gender Bias Analysis** - Gender representation and stereotypes

## Basic Analysis

### Simple Analysis Command

```bash
langquality analyze --input data.csv --output results --language eng
```

This runs all analyzers with default settings.

### Specifying Input Format

LangQuality auto-detects file formats, but you can be explicit:

```bash
# CSV file
langquality analyze -i data.csv -o results -l eng

# JSON file
langquality analyze -i data.json -o results -l eng

# Directory of files
langquality analyze -i data_directory/ -o results -l eng

# Text file (one sentence per line)
langquality analyze -i sentences.txt -o results -l eng
```

## Input Data Formats

### CSV Format

The most common format. LangQuality auto-detects the text column:

```csv
text,domain,metadata
"This is a sentence.",education,source1
"Another sentence here.",health,source2
```

Supported column names for text:
- `text`, `sentence`, `phrase`, `content`
- `source_text`, `original_text`
- Any column with "text" in the name

### JSON Format

```json
[
  {
    "text": "This is a sentence.",
    "domain": "education",
    "metadata": {"source": "book1"}
  },
  {
    "text": "Another sentence here.",
    "domain": "health",
    "metadata": {"source": "book2"}
  }
]
```

### JSONL Format (JSON Lines)

```jsonl
{"text": "This is a sentence.", "domain": "education"}
{"text": "Another sentence here.", "domain": "health"}
```

### Plain Text Format

One sentence per line:

```text
This is the first sentence.
This is the second sentence.
This is the third sentence.
```

## Understanding Analysis Results

### Structural Analysis

Evaluates sentence structure and length:

**Metrics:**
- Average word count per sentence
- Average character count per sentence
- Sentence length distribution
- Outliers (too short or too long)

**Quality Indicators:**
- ✅ **Good**: 5-15 words per sentence
- ⚠️ **Warning**: 3-5 or 15-20 words
- ❌ **Poor**: <3 or >20 words

**Example Output:**
```json
{
  "structural": {
    "total_sentences": 1000,
    "avg_word_count": 12.5,
    "avg_char_count": 75.3,
    "word_distribution": {
      "min": 2,
      "max": 25,
      "median": 11,
      "std": 4.2
    },
    "too_short": 15,
    "too_long": 8,
    "outliers": [...]
  }
}
```

### Linguistic Analysis

Assesses readability and complexity:

**Metrics:**
- Flesch-Kincaid readability score
- Lexical complexity
- Jargon detection
- Sentence complexity

**Quality Indicators:**
- ✅ **Good**: Readability score 40-60
- ⚠️ **Warning**: Score 30-40 or 60-70
- ❌ **Poor**: Score <30 or >70

**Example Output:**
```json
{
  "linguistic": {
    "avg_readability_score": 45.2,
    "readability_distribution": {...},
    "complex_sentences": 12,
    "jargon_detected": {
      "count": 5,
      "terms": ["algorithm", "infrastructure"]
    }
  }
}
```

### Diversity Analysis

Measures vocabulary richness and variety:

**Metrics:**
- Type-Token Ratio (TTR) - unique words / total words
- Unique word count
- N-gram frequency distribution
- Near-duplicate detection

**Quality Indicators:**
- ✅ **Good**: TTR > 0.6
- ⚠️ **Warning**: TTR 0.4-0.6
- ❌ **Poor**: TTR < 0.4

**Example Output:**
```json
{
  "diversity": {
    "type_token_ratio": 0.65,
    "unique_words": 850,
    "total_words": 1300,
    "near_duplicates": 3,
    "duplicate_pairs": [...]
  }
}
```

### Domain Analysis

Evaluates thematic distribution:

**Metrics:**
- Domain representation percentages
- Under-represented domains (<10%)
- Over-represented domains (>30%)
- Balance score

**Quality Indicators:**
- ✅ **Good**: All domains 10-30%
- ⚠️ **Warning**: Some domains 5-10% or 30-40%
- ❌ **Poor**: Domains <5% or >40%

**Example Output:**
```json
{
  "domain": {
    "domain_counts": {
      "education": 300,
      "health": 250,
      "agriculture": 200,
      "commerce": 150,
      "technology": 100
    },
    "domain_percentages": {
      "education": 30.0,
      "health": 25.0,
      "agriculture": 20.0,
      "commerce": 15.0,
      "technology": 10.0
    },
    "underrepresented": [],
    "overrepresented": ["education"],
    "balance_score": 0.85
  }
}
```

### Gender Bias Analysis

Detects gender representation issues:

**Metrics:**
- Gender mention ratio (female/male)
- Stereotype detection
- Gendered profession distribution
- Balance score

**Quality Indicators:**
- ✅ **Good**: Ratio 0.4-0.6
- ⚠️ **Warning**: Ratio 0.3-0.4 or 0.6-0.7
- ❌ **Poor**: Ratio <0.3 or >0.7

**Example Output:**
```json
{
  "gender_bias": {
    "gender_ratio": 0.52,
    "female_mentions": 156,
    "male_mentions": 300,
    "stereotypes_detected": 5,
    "stereotype_examples": [
      "nurse (always female)",
      "engineer (always male)"
    ],
    "bias_score": 0.15
  }
}
```

## Customizing Analysis

### Using Configuration Files

Create a custom configuration file:

```yaml
# my_config.yaml
thresholds:
  structural:
    min_words: 5
    max_words: 15
    min_chars: 20
    max_chars: 150
  
  linguistic:
    max_readability_score: 55
    enable_pos_tagging: true
  
  diversity:
    target_ttr: 0.65
    min_unique_words: 200
    check_duplicates: true
  
  domain:
    min_representation: 0.15
    max_representation: 0.25
  
  gender:
    target_ratio: [0.45, 0.55]
    check_stereotypes: true
```

Use the configuration:

```bash
langquality analyze -i data.csv -o results -l eng -c my_config.yaml
```

### Enabling/Disabling Analyzers

Disable specific analyzers:

```yaml
# config.yaml
analyzers:
  enabled:
    - structural
    - linguistic
    - diversity
  disabled:
    - domain
    - gender_bias
```

### Language-Specific Settings

Different languages may need different thresholds:

```yaml
# For agglutinative languages (longer words)
thresholds:
  structural:
    max_chars: 250  # Allow longer character counts
```

## Advanced Analysis

### Batch Processing

Process multiple files:

```bash
# Process all CSV files in a directory
langquality analyze -i data_dir/ -o results -l eng

# Process specific file pattern
langquality analyze -i "data/*.csv" -o results -l eng
```

### Multi-Language Analysis

Analyze datasets in different languages:

```bash
# Analyze French data
langquality analyze -i french_data.csv -o results_fr -l fra

# Analyze Fongbe data
langquality analyze -i fongbe_data.csv -o results_fon -l fon

# Compare results across languages
langquality compare results_fr results_fon
```

### Incremental Analysis

Analyze new data and compare with baseline:

```bash
# Initial analysis (baseline)
langquality analyze -i baseline.csv -o baseline_results -l eng

# New data analysis
langquality analyze -i new_data.csv -o new_results -l eng

# Compare
langquality compare baseline_results new_results
```

## Interpreting Recommendations

LangQuality generates actionable recommendations based on analysis results.

### Recommendation Severity Levels

- 🔴 **Critical**: Must fix (blocks quality goals)
- 🟡 **Warning**: Should fix (impacts quality)
- 🔵 **Info**: Consider fixing (minor improvements)

### Common Recommendations

#### 1. Sentence Length Issues

**Recommendation:**
> "15 sentences are too short (<3 words). Expand these sentences to improve recording quality."

**Action:**
- Review flagged sentences in `filtered_sentences.csv`
- Expand short sentences with more context
- Aim for 5-15 words per sentence

#### 2. Low Vocabulary Diversity

**Recommendation:**
> "Type-Token Ratio is 0.45 (target: 0.6). Add more diverse vocabulary."

**Action:**
- Include varied expressions for common concepts
- Add domain-specific terminology
- Avoid repetitive phrasing

#### 3. Domain Imbalance

**Recommendation:**
> "Domain 'technology' is under-represented (5%). Collect more sentences in this domain."

**Action:**
- Identify under-represented domains
- Collect additional sentences for those domains
- Aim for 10-30% per domain

#### 4. Gender Bias

**Recommendation:**
> "Gender ratio is 0.25 (target: 0.4-0.6). Include more female representation."

**Action:**
- Review gendered language usage
- Balance pronoun usage
- Diversify professional role examples

## Output Files Reference

### 1. dashboard.html

Interactive HTML dashboard with:
- Summary statistics
- Visual charts and graphs
- Detailed metrics per analyzer
- Recommendations list

**Usage:** Open in any modern web browser

### 2. analysis_results.json

Complete analysis results in JSON format.

**Usage:** 
- Programmatic access to metrics
- Integration with other tools
- Custom reporting

### 3. annotated_sentences.csv

Original sentences with quality annotations:

```csv
text,domain,word_count,char_count,readability_score,quality_flag,issues
"Good sentence.",test,2,15,55.2,TOO_SHORT,"Expand sentence"
"This is a perfect length sentence.",test,6,35,48.1,OK,""
```

**Usage:**
- Review individual sentence quality
- Filter by quality flags
- Identify specific issues

### 4. filtered_sentences.csv

Sentences that failed quality checks:

```csv
text,domain,rejection_reason,severity,suggested_action
"Hi",greeting,TOO_SHORT,critical,"Expand to at least 3 words"
"This is an extremely long...",test,TOO_LONG,warning,"Split into multiple sentences"
```

**Usage:**
- Focus on problematic sentences
- Prioritize fixes by severity
- Track improvement progress

### 5. quality_report.pdf

Summary report with key visualizations (optional).

**Usage:**
- Share with stakeholders
- Documentation
- Progress tracking

### 6. execution_log.txt

Detailed execution log:

```
2024-03-20 10:30:00 - INFO - Starting analysis
2024-03-20 10:30:01 - INFO - Loaded 1000 sentences
2024-03-20 10:30:05 - INFO - Structural analysis complete
2024-03-20 10:30:10 - INFO - Linguistic analysis complete
...
```

**Usage:**
- Debugging
- Performance monitoring
- Audit trail

## Best Practices

### 1. Iterative Improvement

```bash
# Initial analysis
langquality analyze -i data_v1.csv -o results_v1 -l eng

# Review recommendations
cat results_v1/analysis_results.json | jq '.recommendations'

# Fix issues and re-analyze
langquality analyze -i data_v2.csv -o results_v2 -l eng

# Compare improvements
langquality compare results_v1 results_v2
```

### 2. Focus on Critical Issues First

1. Review dashboard for critical (red) recommendations
2. Fix structural issues (length, formatting)
3. Address diversity and balance
4. Fine-tune linguistic complexity

### 3. Use Custom Configurations

Create project-specific configurations:

```bash
# ASR project
langquality analyze -i asr_data.csv -o asr_results -l fon -c configs/asr_config.yaml

# Translation project
langquality analyze -i translation_data.csv -o trans_results -l fra -c configs/translation_config.yaml
```

### 4. Track Progress Over Time

```bash
# Save results with timestamps
langquality analyze -i data.csv -o results_$(date +%Y%m%d) -l eng

# Compare with previous version
langquality compare results_20240301 results_20240315
```

## Next Steps

- [Configuration Guide](../configuration_guide.md) - Detailed configuration options
- [Language Pack Guide](../language_pack_guide.md) - Work with different languages
- [FAQ](../faq.md) - Common questions and solutions
