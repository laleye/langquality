# LangQuality Quick Start Guide

Welcome to LangQuality! This guide will help you get started with analyzing text data quality for low-resource languages in just a few minutes.

## What is LangQuality?

LangQuality is a language-agnostic toolkit for analyzing the quality of text datasets. Originally designed for Fongbe (a low-resource language from Benin), it now supports any language through a flexible Language Pack system.

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- 500MB disk space (for language models and resources)

### Install from PyPI

```bash
pip install langquality
```

### Install from Source

```bash
git clone https://github.com/langquality/langquality-toolkit.git
cd langquality-toolkit
pip install -e .
```

### Install Language-Specific Dependencies

Some language packs require additional dependencies (like spaCy models):

```bash
# For French language pack
python -m spacy download fr_core_news_md

# For English language pack
python -m spacy download en_core_web_md
```

## Your First Analysis

### Step 1: Prepare Your Data

Create a CSV file with your text data. For example, `my_data.csv`:

```csv
text,domain
"Hello, how are you today?",greeting
"The weather is beautiful.",conversation
"I need to buy groceries.",daily_life
```

The file should have:
- A text column (can be named `text`, `sentence`, `phrase`, etc.)
- Optionally, a `domain` column for thematic categorization

### Step 2: Run Analysis

```bash
langquality analyze --input my_data.csv --output results --language eng
```

This command:
- Loads your data from `my_data.csv`
- Uses the English language pack (`eng`)
- Analyzes text quality across multiple dimensions
- Saves results to the `results/` directory

### Step 3: View Results

Open the interactive dashboard:

```bash
# On Linux/Mac
open results/dashboard.html

# On Windows
start results/dashboard.html
```

The dashboard shows:
- **Structural metrics**: Sentence length distribution, outliers
- **Linguistic metrics**: Readability scores, complexity
- **Diversity metrics**: Vocabulary richness, duplicates
- **Domain balance**: Distribution across categories
- **Gender bias**: Gender representation (if applicable)
- **Recommendations**: Actionable suggestions for improvement

## Working with Language Packs

### List Available Language Packs

```bash
langquality pack list
```

Output:
```
Available Language Packs:
  fon - Fongbe (Niger-Congo) [stable]
  eng - English (Indo-European) [stable]
  fra - French (Indo-European) [stable]
```

### View Language Pack Details

```bash
langquality pack info fon
```

Output:
```
Language Pack: Fongbe (fon)
Family: Niger-Congo
Script: Latin
Status: stable
Version: 1.0.0

Resources:
  ✓ Lexicon (5,000 words)
  ✓ Gender terms
  ✓ Professions
  ✓ ASR vocabulary

Analyzers:
  ✓ Structural
  ✓ Linguistic
  ✓ Diversity
  ✓ Domain
  ✓ Gender Bias
```

### Analyze with Different Languages

```bash
# Analyze French text
langquality analyze -i french_data.csv -o results_fr --language fra

# Analyze Fongbe text
langquality analyze -i fongbe_data.csv -o results_fon --language fon
```

## Understanding the Output

After analysis, you'll find these files in your output directory:

### 1. `dashboard.html`
Interactive HTML dashboard with visualizations. Open in any modern browser.

### 2. `analysis_results.json`
Detailed metrics in JSON format:

```json
{
  "metadata": {
    "language": "eng",
    "total_sentences": 150,
    "analysis_date": "2024-03-20T10:30:00"
  },
  "structural": {
    "avg_word_count": 12.5,
    "too_short": 5,
    "too_long": 3
  },
  "linguistic": {
    "avg_readability": 45.2
  },
  "diversity": {
    "type_token_ratio": 0.65,
    "unique_words": 450
  },
  "recommendations": [...]
}
```

### 3. `annotated_sentences.csv`
Your original data with quality scores:

```csv
text,domain,word_count,readability_score,quality_flag
"Hello, how are you?",greeting,4,55.2,OK
"This is a very long sentence...",conversation,25,42.1,TOO_LONG
```

### 4. `filtered_sentences.csv`
Sentences that failed quality checks:

```csv
text,domain,rejection_reason,suggested_action
"Hi",greeting,TOO_SHORT,"Expand to at least 3 words"
```

### 5. `quality_report.pdf`
Summary report with key metrics and visualizations (if PDF export is enabled).

## Common Use Cases

### Use Case 1: ASR Dataset Preparation

Preparing text for speech recording:

```bash
langquality analyze \
  --input asr_sentences.csv \
  --output asr_results \
  --language fon \
  --config config/asr_config.yaml
```

Create `config/asr_config.yaml`:
```yaml
thresholds:
  structural:
    min_words: 5
    max_words: 15  # Optimal for recording
  linguistic:
    max_readability_score: 50  # Keep it simple
```

### Use Case 2: Translation Dataset Quality

Checking parallel corpus quality:

```bash
langquality analyze \
  --input source_text.csv \
  --output translation_check \
  --language fra
```

### Use Case 3: Multi-Domain Balance

Ensuring balanced representation:

```bash
langquality analyze \
  --input multi_domain.csv \
  --output balance_check \
  --language eng
```

Check the domain distribution in the dashboard to identify under-represented topics.

## Next Steps

Now that you've completed your first analysis, explore:

1. **[User Guide](user_guide/)** - Detailed documentation on all features
2. **[Language Pack Guide](language_pack_guide.md)** - Create packs for new languages
3. **[Configuration Guide](configuration_guide.md)** - Customize analysis parameters
4. **[FAQ](faq.md)** - Common questions and solutions

## Getting Help

- **Documentation**: [https://langquality.readthedocs.io](https://langquality.readthedocs.io)
- **GitHub Issues**: [https://github.com/langquality/langquality-toolkit/issues](https://github.com/langquality/langquality-toolkit/issues)
- **Discussions**: [https://github.com/langquality/langquality-toolkit/discussions](https://github.com/langquality/langquality-toolkit/discussions)

## Quick Reference

### Essential Commands

```bash
# Analyze data
langquality analyze -i INPUT -o OUTPUT --language LANG

# List language packs
langquality pack list

# Get pack info
langquality pack info LANG_CODE

# Create new pack template
langquality pack create LANG_CODE

# Validate a pack
langquality pack validate PATH
```

### Common Options

- `-i, --input`: Input file or directory
- `-o, --output`: Output directory
- `-l, --language`: Language code (ISO 639-3)
- `-c, --config`: Custom configuration file
- `--help`: Show help message

Happy analyzing! 🚀
