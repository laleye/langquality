# Fongbe Data Quality Pipeline - User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [CLI Commands and Options](#cli-commands-and-options)
4. [Input Data Format](#input-data-format)
5. [Configuration](#configuration)
6. [Understanding Metrics](#understanding-metrics)
7. [Interpreting the Dashboard](#interpreting-the-dashboard)
8. [Recommendations](#recommendations)
9. [Export Formats](#export-formats)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)

## Introduction

The Fongbe Data Quality Pipeline is designed to help linguists and data collectors evaluate the quality of French text data before translation to Fongbe and audio recording. The tool provides comprehensive analysis across multiple dimensions:

- **Structural quality**: Sentence length and formatting
- **Linguistic quality**: Readability and complexity
- **Diversity**: Vocabulary richness and variety
- **Balance**: Domain and gender representation
- **Actionability**: Specific recommendations for improvement

This guide will walk you through every aspect of using the pipeline effectively.

## Installation

### System Requirements

- **Operating System**: Linux, macOS, or Windows
- **Python**: Version 3.8 or higher
- **RAM**: Minimum 2GB (4GB recommended for large datasets)
- **Disk Space**: 500MB for dependencies and language models

### Step-by-Step Installation

#### 1. Install Python

Ensure Python 3.8+ is installed:

```bash
python --version
# Should show Python 3.8.0 or higher
```

If not installed, download from [python.org](https://www.python.org/downloads/)

#### 2. Clone or Download the Repository

```bash
git clone https://github.com/yourusername/fongbe-data-quality.git
cd fongbe-data-quality
```

#### 3. Create a Virtual Environment (Recommended)

Virtual environments keep dependencies isolated:

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Your prompt should now show (venv)
```

#### 4. Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# This installs:
# - pandas, numpy (data processing)
# - spacy (NLP)
# - plotly (visualizations)
# - pyyaml (configuration)
# - reportlab (PDF generation)
# - click (CLI)
# - and more...
```

#### 5. Download Language Model

The pipeline requires spaCy's French language model:

```bash
python -m spacy download fr_core_news_md
```

This downloads ~40MB of French language data for linguistic analysis.

#### 6. Install the Package

```bash
# Install in development mode
pip install -e .
```

#### 7. Verify Installation

```bash
# Check CLI is available
fongbe-quality --help

# Should display help message with available commands
```

## CLI Commands and Options

### Main Command: `analyze`

The primary command for running the quality analysis pipeline.

**Syntax:**
```bash
fongbe-quality analyze [OPTIONS]
```

**Required Options:**

- `--input PATH` or `-i PATH`
  - Path to directory containing CSV files with French sentences
  - Can be relative or absolute path
  - Example: `--input data/sentences`

- `--output PATH` or `-o PATH`
  - Path to directory where results will be saved
  - Directory will be created if it doesn't exist
  - Example: `--output results/analysis_2024`

**Optional Options:**

- `--config PATH` or `-c PATH`
  - Path to custom YAML configuration file
  - If not provided, uses default configuration
  - Example: `--config config/my_settings.yaml`

- `--help`
  - Display help message and exit
  - Shows all available options

**Usage Examples:**

```bash
# Basic analysis with default settings
fongbe-quality analyze --input data/sentences --output results

# Short form
fongbe-quality analyze -i data/sentences -o results

# With custom configuration
fongbe-quality analyze -i data/sentences -o results -c my_config.yaml

# Using absolute paths
fongbe-quality analyze \
  --input /home/user/project/data \
  --output /home/user/project/results

# Analyze test data
fongbe-quality analyze -i tests/data/small_dataset -o test_results
```

**What Happens When You Run `analyze`:**

1. **Loading**: Reads all CSV files from input directory
2. **Validation**: Checks data format and encoding
3. **Analysis**: Runs all enabled analyzers sequentially
4. **Recommendations**: Generates actionable suggestions
5. **Export**: Creates all output files (dashboard, JSON, CSV, PDF)
6. **Summary**: Displays key findings in terminal

**Expected Output:**

```
Loading data from data/sentences...
Found 5 CSV files with 1,247 sentences

Running analyzers...
✓ Structural analysis complete
✓ Linguistic analysis complete
✓ Diversity analysis complete
✓ Domain analysis complete
✓ Gender bias analysis complete

Generating recommendations...
Found 8 recommendations (3 critical, 5 warnings)

Exporting results...
✓ Dashboard: results/dashboard.html
✓ JSON: results/analysis_results.json
✓ Annotated CSV: results/annotated_sentences.csv
✓ Filtered CSV: results/filtered_sentences.csv
✓ PDF Report: results/report.pdf
✓ Execution Log: results/execution_log.txt

Analysis complete! Open results/dashboard.html to view results.
```

## Input Data Format

### CSV File Structure

The pipeline expects CSV files containing French sentences. Each file should represent a thematic domain.

**Minimum Requirements:**
- At least one column containing text sentences
- UTF-8 encoding (or other common encodings - auto-detected)
- One sentence per row

**Supported Column Names:**

The pipeline automatically detects text columns with these names:
- `sentence`
- `text`
- `phrase`
- `content`
- `french`
- `source`

**Example 1: Simple Format**

File: `education.csv`
```csv
sentence
"Les élèves étudient les mathématiques."
"L'enseignant explique la leçon."
"Les enfants jouent dans la cour de récréation."
```

**Example 2: With Additional Columns**

File: `health.csv`
```csv
id,text,category,verified
1,"Le médecin examine le patient.",medical,yes
2,"Prenez ce médicament trois fois par jour.",prescription,yes
3,"L'infirmière prend la tension artérielle.",medical,yes
```

The pipeline will use the `text` column and ignore other columns.

**Example 3: Multiple Domains**

Organize your data by domain using separate files:

```
data/
├── agriculture.csv      # Domain: agriculture
├── commerce.csv         # Domain: commerce
├── education.csv        # Domain: education
├── health.csv          # Domain: health
└── family.csv          # Domain: family
```

**Domain Extraction:**

The domain is automatically extracted from the filename:
- `education.csv` → domain: `education`
- `sante.csv` → domain: `sante`
- `01_agriculture.csv` → domain: `agriculture`

**Encoding:**

The pipeline handles various encodings automatically:
- UTF-8 (recommended)
- Latin-1 (ISO-8859-1)
- Windows-1252
- Other common encodings

**Best Practices for Input Data:**

1. **Use descriptive filenames** that reflect the domain
2. **Keep one domain per file** for accurate domain analysis
3. **Use UTF-8 encoding** when creating CSV files
4. **One sentence per row** - avoid multi-sentence cells
5. **Clean data first** - remove empty rows, fix obvious errors

## Configuration

### Configuration File Format

The pipeline uses YAML configuration files to customize analysis parameters.

### Default Configuration

Located at `config/default_config.yaml`:

```yaml
analysis:
  # Structural thresholds
  min_words: 3
  max_words: 20
  
  # Linguistic thresholds
  min_readability_score: 0
  max_readability_score: 60
  
  # Diversity targets
  target_ttr: 0.6
  
  # Domain balance
  min_domain_representation: 0.10
  max_domain_representation: 0.30
  
  # Gender balance
  target_gender_ratio: [0.4, 0.6]
  
  # Custom jargon terms
  jargon_terms: []
  
  # Reference vocabulary
  reference_vocabulary: null

pipeline:
  language: "fr"
  enable_analyzers:
    - structural
    - linguistic
    - diversity
    - domain
    - gender_bias
```

### Creating Custom Configuration

1. **Copy the example configuration:**

```bash
cp config/example_config.yaml config/my_config.yaml
```

2. **Edit parameters** in `my_config.yaml`

3. **Use in analysis:**

```bash
fongbe-quality analyze -i data -o results -c config/my_config.yaml
```

### Configuration Parameters Explained

#### Structural Analysis Parameters

**`min_words`** (default: 3)
- Minimum number of words per sentence
- Sentences shorter than this are flagged as "too short"
- Rationale: Very short sentences may lack context for translation
- Example: "Bonjour." (1 word) would be flagged

**`max_words`** (default: 20)
- Maximum number of words per sentence
- Sentences longer than this are flagged as "too long"
- Rationale: Long sentences are harder to record clearly and translate accurately
- Example: A 25-word sentence would be flagged

**When to adjust:**
- Increase `max_words` if your domain requires longer explanations
- Decrease `min_words` if short greetings/commands are acceptable

#### Linguistic Analysis Parameters

**`max_readability_score`** (default: 60)
- Maximum Flesch-Kincaid readability score
- Lower scores = easier to read
- Scale: 0-100 (0 = very difficult, 100 = very easy)
- Rationale: Easier sentences are clearer for recording and translation

**`jargon_terms`** (default: [])
- List of technical terms to flag in sentences
- Useful for avoiding domain-specific jargon
- Example: `["algorithme", "infrastructure", "paradigme"]`

**`reference_vocabulary`** (default: null)
- Path to file containing reference vocabulary
- Used to calculate vocabulary coverage
- Format: One word per line

#### Diversity Analysis Parameters

**`target_ttr`** (default: 0.6)
- Target Type-Token Ratio (vocabulary richness)
- Formula: unique_words / total_words
- Range: 0.0 to 1.0
- Higher values = more diverse vocabulary
- Rationale: Rich vocabulary improves model training

**When to adjust:**
- Lower for specialized domains with limited vocabulary
- Higher for general-purpose datasets

#### Domain Analysis Parameters

**`min_domain_representation`** (default: 0.10)
- Minimum percentage for each domain (10%)
- Domains below this are flagged as "underrepresented"
- Rationale: Ensures balanced coverage across topics

**`max_domain_representation`** (default: 0.30)
- Maximum percentage for any single domain (30%)
- Domains above this are flagged as "overrepresented"
- Rationale: Prevents dataset bias toward one topic

**When to adjust:**
- Adjust based on your target domain distribution
- For 5 domains, equal distribution would be 20% each

#### Gender Bias Parameters

**`target_gender_ratio`** (default: [0.4, 0.6])
- Acceptable range for feminine/masculine ratio
- Format: [min, max]
- Example: [0.4, 0.6] means 40-60% feminine mentions is acceptable
- Rationale: Balanced gender representation reduces bias

**When to adjust:**
- Tighten range for stricter balance: [0.45, 0.55]
- Widen for more flexibility: [0.3, 0.7]

### Example Custom Configurations

**Configuration 1: Strict Quality Standards**

```yaml
analysis:
  min_words: 5          # Longer minimum
  max_words: 15         # Shorter maximum
  max_readability_score: 50  # Easier reading
  target_ttr: 0.7       # Higher diversity
  min_domain_representation: 0.15  # More balanced
  max_domain_representation: 0.25
  target_gender_ratio: [0.45, 0.55]  # Stricter balance
```

**Configuration 2: Relaxed for Specialized Domain**

```yaml
analysis:
  min_words: 2          # Allow shorter
  max_words: 25         # Allow longer
  max_readability_score: 70
  target_ttr: 0.5       # Lower diversity OK
  jargon_terms:         # Domain-specific terms
    - "diagnostic"
    - "traitement"
    - "symptôme"
```

## Understanding Metrics

This section explains each metric calculated by the pipeline and how to interpret the results.

### Structural Metrics

#### Total Sentences
- **What it is**: Count of all sentences in the dataset
- **Interpretation**: Larger datasets (1000+) provide better model training

#### Word Distribution
- **mean**: Average words per sentence
- **median**: Middle value when sentences are sorted by length
- **std**: Standard deviation (variability in length)
- **Interpretation**: 
  - Mean 8-12 words is ideal for ASR
  - Low std (<3) suggests repetitive structure
  - High std (>6) suggests inconsistent sentence length

#### Length Histogram
- **What it is**: Frequency distribution of sentence lengths
- **Interpretation**: Should show a bell curve centered around 8-12 words

#### Too Short / Too Long
- **What it is**: Lists of sentences outside acceptable length range
- **Interpretation**: 
  - <5% flagged = good
  - 5-15% flagged = needs attention
  - >15% flagged = significant issue

### Linguistic Metrics

#### Average Readability Score
- **What it is**: Flesch-Kincaid readability score (0-100)
- **Scale**:
  - 90-100: Very easy (5th grade)
  - 60-70: Easy (8th-9th grade)
  - 30-50: Difficult (college level)
  - 0-30: Very difficult (professional)
- **Interpretation**: 
  - Target: 50-70 for clear recording
  - <50: May be too complex
  - >80: May be too simple

#### Lexical Complexity
- **What it is**: Proportion of rare/uncommon words
- **Calculation**: Based on word frequency in reference corpus
- **Interpretation**:
  - Low (<0.2): Common, everyday vocabulary
  - Medium (0.2-0.4): Mixed vocabulary
  - High (>0.4): Many rare/technical terms

#### Jargon Detected
- **What it is**: Count and location of flagged technical terms
- **Interpretation**: 
  - 0 instances: Good for general dataset
  - <5%: Acceptable
  - >10%: Consider simplifying or removing

#### Complex Syntax
- **What it is**: Sentences with multiple clauses, passive voice, etc.
- **Interpretation**:
  - <10%: Good
  - 10-20%: Acceptable
  - >20%: Consider simplifying

### Diversity Metrics

#### Type-Token Ratio (TTR)
- **What it is**: Ratio of unique words to total words
- **Formula**: unique_words / total_words
- **Interpretation**:
  - <0.4: Low diversity, repetitive
  - 0.4-0.6: Moderate diversity
  - >0.6: High diversity, rich vocabulary
- **Target**: 0.6 or higher

#### Unique Words
- **What it is**: Count of distinct words in dataset
- **Interpretation**: 
  - More unique words = better vocabulary coverage
  - Compare to total words for TTR

#### Vocabulary Coverage
- **What it is**: Percentage of reference vocabulary present
- **Interpretation**:
  - >80%: Excellent coverage
  - 60-80%: Good coverage
  - <60%: Missing common words

#### N-gram Analysis
- **What it is**: Frequency of word sequences (2-grams, 3-grams)
- **Interpretation**:
  - Top n-grams should be common phrases ("il y a", "c'est un")
  - High repetition of specific n-grams suggests lack of variety

#### Near Duplicates
- **What it is**: Pairs of sentences with >80% similarity
- **Interpretation**:
  - 0 duplicates: Excellent
  - <5%: Acceptable
  - >5%: Remove duplicates

#### Sentence Starter Diversity
- **What it is**: Variety in how sentences begin
- **Interpretation**:
  - High diversity: Good structural variety
  - Low diversity: Repetitive sentence patterns

### Domain Metrics

#### Domain Counts
- **What it is**: Number of sentences per domain
- **Interpretation**: Should be relatively balanced across domains

#### Domain Percentages
- **What it is**: Proportion of dataset from each domain
- **Interpretation**:
  - Ideal: 10-30% per domain
  - <10%: Underrepresented
  - >30%: Overrepresented

#### Underrepresented Domains
- **What it is**: Domains with <10% of total sentences
- **Action**: Collect more data for these domains

#### Overrepresented Domains
- **What it is**: Domains with >30% of total sentences
- **Action**: Consider reducing or balancing with other domains

### Gender Bias Metrics

#### Masculine/Feminine Counts
- **What it is**: Count of gendered terms (pronouns, articles, nouns)
- **Examples**:
  - Masculine: il, le, un, homme, père
  - Feminine: elle, la, une, femme, mère

#### Gender Ratio
- **What it is**: Ratio of feminine to masculine mentions
- **Formula**: feminine_count / masculine_count
- **Interpretation**:
  - 0.4-0.6: Balanced
  - <0.4: Male-biased
  - >0.6: Female-biased

#### Stereotypes Detected
- **What it is**: Gendered profession associations
- **Examples**:
  - Stereotype: "L'infirmière" (nurse always feminine)
  - Balanced: "Le médecin" and "La médecin" both present
- **Interpretation**: Fewer stereotypes = better balance

#### Bias Score
- **What it is**: Overall bias metric (0-1)
- **Scale**:
  - 0.0-0.2: Well balanced
  - 0.2-0.4: Moderate bias
  - >0.4: Significant bias
- **Action**: >0.3 requires attention

## Interpreting the Dashboard

The dashboard provides an interactive visualization of all metrics. This section explains each section.

### Dashboard Structure

The dashboard is organized into these sections:

1. **Overview** - Summary statistics
2. **Structural Analysis** - Length distributions
3. **Linguistic Complexity** - Readability and complexity
4. **Diversity Metrics** - Vocabulary and variety
5. **Domain Distribution** - Thematic balance
6. **Gender Bias Analysis** - Gender representation
7. **Recommendations** - Actionable suggestions

### Overview Section

**Key Metrics Displayed:**
- Total sentences analyzed
- Average sentence length
- Overall quality score
- Number of critical issues

**How to Read:**
- Green indicators: Metrics within target range
- Yellow indicators: Metrics needing attention
- Red indicators: Critical issues requiring action

### Structural Analysis Section

**Visualizations:**

1. **Length Distribution Histogram**
   - X-axis: Number of words
   - Y-axis: Frequency (number of sentences)
   - Ideal: Bell curve centered at 8-12 words
   - Red zones: Too short (<3) or too long (>20)

2. **Statistical Summary Table**
   - Shows mean, median, std, min, max
   - Compare mean vs median to detect skew

**Interpretation Tips:**
- Bimodal distribution: Two distinct sentence types
- Right skew: Many long sentences
- Left skew: Many short sentences

### Linguistic Complexity Section

**Visualizations:**

1. **Readability Score Distribution**
   - Shows spread of Flesch-Kincaid scores
   - Target zone: 50-70 (highlighted in green)

2. **Complexity Indicators**
   - Color-coded bars for different complexity measures
   - Green: Low complexity (good)
   - Yellow: Medium complexity
   - Red: High complexity (problematic)

3. **Jargon Detection Table**
   - Lists flagged technical terms
   - Shows frequency and example sentences

**Interpretation Tips:**
- Wide distribution: Inconsistent complexity
- Many red indicators: Dataset too complex
- Check jargon table for specific terms to avoid

### Diversity Metrics Section

**Visualizations:**

1. **Type-Token Ratio Gauge**
   - Shows TTR value with target zone
   - Green zone: >0.6
   - Yellow zone: 0.4-0.6
   - Red zone: <0.4

2. **Top N-grams Chart**
   - Bar chart of most frequent word sequences
   - Check for over-repetition

3. **Vocabulary Coverage**
   - Percentage of reference vocabulary covered
   - Shows gaps in vocabulary

4. **Near Duplicates List**
   - Table of similar sentence pairs
   - Shows similarity percentage

**Interpretation Tips:**
- Low TTR + high n-gram repetition = need more variety
- Low vocabulary coverage = missing common words
- Many near duplicates = remove redundant sentences

### Domain Distribution Section

**Visualizations:**

1. **Domain Pie Chart**
   - Shows proportion of each domain
   - Color-coded by representation status
   - Green: Well represented (10-30%)
   - Yellow: Borderline
   - Red: Under/over represented

2. **Domain Balance Table**
   - Lists each domain with count and percentage
   - Flags underrepresented (<10%) and overrepresented (>30%)

**Interpretation Tips:**
- Uneven pie chart = imbalanced dataset
- Check flagged domains for collection priorities
- Aim for relatively equal slices

### Gender Bias Analysis Section

**Visualizations:**

1. **Gender Ratio Gauge**
   - Shows F/M ratio with target zone (0.4-0.6)
   - Indicates bias direction

2. **Gender Mentions Bar Chart**
   - Compares masculine vs feminine counts
   - Should be relatively balanced

3. **Stereotype Detection Table**
   - Lists detected stereotypical associations
   - Shows sentence examples

**Interpretation Tips:**
- Ratio outside 0.4-0.6: Collect more balanced data
- Many stereotypes: Review and diversify examples
- Check specific professions for balance

### Recommendations Section

**Structure:**
- Recommendations sorted by priority (1-5)
- Color-coded by severity:
  - Red: Critical (must fix)
  - Yellow: Warning (should fix)
  - Blue: Info (nice to fix)

**Each Recommendation Includes:**
- **Title**: Brief description of issue
- **Category**: Which analyzer detected it
- **Severity**: Critical/Warning/Info
- **Description**: Detailed explanation
- **Affected Items**: Specific sentences/domains/terms
- **Suggested Actions**: Concrete steps to resolve

**How to Use:**
1. Start with critical recommendations
2. Address warnings that affect multiple metrics
3. Use suggested actions as a checklist
4. Re-run analysis after making changes

## Recommendations

### Understanding Recommendation Types

#### Structural Recommendations

**"Too many long sentences"**
- **Cause**: >15% of sentences exceed max_words threshold
- **Impact**: Difficult to record clearly, hard to translate
- **Actions**:
  - Split long sentences into shorter ones
  - Remove unnecessary clauses
  - Simplify complex constructions

**"Too many short sentences"**
- **Cause**: >15% of sentences below min_words threshold
- **Impact**: Lack context for translation
- **Actions**:
  - Expand short sentences with more detail
  - Combine related short sentences
  - Add context where needed

#### Linguistic Recommendations

**"High complexity detected"**
- **Cause**: Many sentences with readability score <50
- **Impact**: Difficult for speakers to pronounce clearly
- **Actions**:
  - Simplify vocabulary
  - Use active voice instead of passive
  - Break complex sentences into simpler ones

**"Jargon terms detected"**
- **Cause**: Technical terms found in sentences
- **Impact**: May not translate well, unclear pronunciation
- **Actions**:
  - Replace jargon with common terms
  - Remove highly technical sentences
  - Add glossary if jargon is necessary

#### Diversity Recommendations

**"Low vocabulary diversity"**
- **Cause**: TTR below target (e.g., <0.6)
- **Impact**: Limited vocabulary coverage for model training
- **Actions**:
  - Add sentences with varied vocabulary
  - Avoid repetitive phrasing
  - Include synonyms and varied expressions

**"High n-gram repetition"**
- **Cause**: Same word sequences appear frequently
- **Impact**: Structural monotony, limited pattern learning
- **Actions**:
  - Vary sentence structures
  - Use different ways to express similar ideas
  - Review and diversify sentence starters

**"Near duplicates found"**
- **Cause**: Multiple very similar sentences
- **Impact**: Wasted data, no new information
- **Actions**:
  - Remove duplicate sentences
  - Keep only the best version
  - Replace with new, unique sentences

**"Low vocabulary coverage"**
- **Cause**: Missing common words from reference vocabulary
- **Impact**: Incomplete language representation
- **Actions**:
  - Identify missing word categories
  - Add sentences using missing words
  - Focus on common, everyday vocabulary

#### Domain Recommendations

**"Underrepresented domains"**
- **Cause**: Some domains have <10% of sentences
- **Impact**: Unbalanced topic coverage
- **Actions**:
  - Collect more sentences for flagged domains
  - Aim for 15-25% per domain
  - Ensure real-world relevance

**"Overrepresented domains"**
- **Cause**: One domain has >30% of sentences
- **Impact**: Dataset bias toward one topic
- **Actions**:
  - Reduce sentences from overrepresented domain
  - Balance with other domains
  - Consider splitting large domains into subcategories

#### Gender Bias Recommendations

**"Gender imbalance detected"**
- **Cause**: F/M ratio outside target range (0.4-0.6)
- **Impact**: Biased representation, potential model bias
- **Actions**:
  - Add sentences with underrepresented gender
  - Balance pronoun usage
  - Include diverse examples for both genders

**"Stereotypical associations found"**
- **Cause**: Professions consistently associated with one gender
- **Impact**: Reinforces stereotypes
- **Actions**:
  - Add counter-examples (e.g., male nurses, female engineers)
  - Use gender-neutral terms where possible
  - Diversify professional roles

### Prioritizing Recommendations

**Priority 1 (Critical):**
- Structural issues affecting >20% of sentences
- Very low TTR (<0.4)
- Severe domain imbalance (one domain >50%)
- Extreme gender bias (ratio <0.3 or >0.7)

**Priority 2 (High):**
- Moderate structural issues (10-20% affected)
- Low vocabulary coverage (<60%)
- Domain imbalance (underrepresented <5%)
- Moderate gender bias (ratio 0.3-0.4 or 0.6-0.7)

**Priority 3 (Medium):**
- Minor structural issues (<10% affected)
- Some jargon detected
- N-gram repetition
- Near duplicates present

**Priority 4-5 (Low):**
- Fine-tuning recommendations
- Optimization suggestions
- Nice-to-have improvements

## Export Formats

### JSON Export

**File**: `analysis_results.json`

**Content**: Complete analysis results in structured format

**Use Cases:**
- Programmatic access to metrics
- Integration with other tools
- Detailed analysis
- Record keeping

**Structure:**
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "config": {...},
  "structural": {
    "total_sentences": 1000,
    "word_distribution": {...},
    "too_short": [...],
    "too_long": [...]
  },
  "linguistic": {...},
  "diversity": {...},
  "domain": {...},
  "gender_bias": {...},
  "recommendations": [...]
}
```

**How to Use:**
```python
import json

# Load results
with open('results/analysis_results.json', 'r') as f:
    results = json.load(f)

# Access specific metrics
ttr = results['diversity']['ttr']
avg_length = results['structural']['word_distribution']['mean']
```

### Annotated CSV Export

**File**: `annotated_sentences.csv`

**Content**: Original sentences with quality scores and flags

**Use Cases:**
- Review individual sentences
- Filter by quality score
- Identify specific problematic sentences
- Manual review and editing

**Columns:**
- `sentence`: Original text
- `domain`: Thematic category
- `source_file`: Original CSV file
- `line_number`: Position in source file
- `word_count`: Number of words
- `char_count`: Number of characters
- `readability_score`: Flesch-Kincaid score
- `quality_flag`: OK, TOO_SHORT, TOO_LONG, COMPLEX, etc.
- `issues`: List of detected issues

**Example:**
```csv
sentence,domain,word_count,readability_score,quality_flag,issues
"Bonjour comment allez-vous",greeting,4,65.2,OK,""
"Cette phrase est beaucoup trop longue et contient...",test,25,42.1,TOO_LONG,"length"
"Salut",greeting,1,80.0,TOO_SHORT,"length"
```

**How to Use:**
```python
import pandas as pd

# Load annotated data
df = pd.read_csv('results/annotated_sentences.csv')

# Filter problematic sentences
problems = df[df['quality_flag'] != 'OK']

# Get sentences by domain
education = df[df['domain'] == 'education']

# Sort by readability
sorted_df = df.sort_values('readability_score')
```

### Filtered CSV Export

**File**: `filtered_sentences.csv`

**Content**: Only sentences that failed quality checks

**Use Cases:**
- Focus on problematic sentences
- Prioritize editing efforts
- Understand common issues
- Track improvements over iterations

**Columns:**
- `sentence`: Original text
- `domain`: Thematic category
- `source_file`: Original file
- `line_number`: Position in source
- `rejection_reason`: Why it was flagged
- `suggested_action`: How to fix it

**Example:**
```csv
sentence,domain,rejection_reason,suggested_action
"Salut",greeting,TOO_SHORT,"Expand to at least 3 words"
"Cette phrase contient...",test,TOO_LONG,"Split into 2-3 shorter sentences"
"L'algorithme optimise...",tech,JARGON,"Replace 'algorithme' with simpler term"
```

### PDF Report Export

**File**: `report.pdf`

**Content**: Professional summary report with key visualizations

**Use Cases:**
- Share with stakeholders
- Documentation
- Presentations
- Archive analysis results

**Sections:**
1. Executive Summary
2. Key Metrics Overview
3. Structural Analysis (with charts)
4. Linguistic Quality
5. Diversity Assessment
6. Domain Balance
7. Gender Bias Analysis
8. Top Recommendations
9. Methodology Notes

### Execution Log

**File**: `execution_log.txt`

**Content**: Timestamped record of analysis execution

**Use Cases:**
- Debugging
- Audit trail
- Performance monitoring
- Configuration tracking

**Example:**
```
=== Fongbe Quality Pipeline Execution Log ===
Timestamp: 2024-01-15 10:30:00
Configuration: config/default_config.yaml

Input: data/sentences (5 files, 1,247 sentences)
Output: results/

Analyzers Run:
- StructuralAnalyzer: 1.2s
- LinguisticAnalyzer: 3.4s
- DiversityAnalyzer: 2.1s
- DomainAnalyzer: 0.5s
- GenderBiasAnalyzer: 1.8s

Total Analysis Time: 9.0s

Results:
- 8 recommendations generated
- 3 critical issues
- 5 warnings

Outputs Created:
- dashboard.html
- analysis_results.json
- annotated_sentences.csv
- filtered_sentences.csv
- report.pdf

Status: SUCCESS
```

## Best Practices

### Data Collection Workflow

**Phase 1: Initial Collection**
1. Define target domains (5-10 domains)
2. Set collection goals (sentences per domain)
3. Collect initial dataset (aim for 500+ sentences)
4. Organize by domain (one CSV per domain)

**Phase 2: First Analysis**
1. Run pipeline with default configuration
2. Review dashboard for major issues
3. Note critical recommendations
4. Identify gaps (domains, vocabulary, balance)

**Phase 3: Iterative Improvement**
1. Address critical issues first
2. Collect additional data for underrepresented domains
3. Remove or revise problematic sentences
4. Re-run analysis
5. Repeat until quality targets met

**Phase 4: Final Validation**
1. Run with strict configuration
2. Verify all metrics in target ranges
3. Manual review of filtered sentences
4. Final cleanup and organization

### Quality Targets

**Structural Quality:**
- ✓ <5% sentences flagged as too short/long
- ✓ Mean sentence length: 8-12 words
- ✓ Standard deviation: 3-5 words

**Linguistic Quality:**
- ✓ Average readability: 50-70
- ✓ <5% sentences with jargon
- ✓ <10% complex syntax

**Diversity:**
- ✓ TTR ≥ 0.6
- ✓ Vocabulary coverage ≥ 70%
- ✓ <2% near duplicates
- ✓ No single n-gram >5% frequency

**Domain Balance:**
- ✓ Each domain: 10-30% of total
- ✓ No domain <5% or >35%
- ✓ At least 5 different domains

**Gender Balance:**
- ✓ F/M ratio: 0.4-0.6
- ✓ <5 stereotypical associations
- ✓ Bias score <0.2

### Sentence Writing Guidelines

**DO:**
- ✓ Write clear, natural sentences
- ✓ Use common, everyday vocabulary
- ✓ Vary sentence structures
- ✓ Include diverse topics and contexts
- ✓ Balance gender representation
- ✓ Use active voice
- ✓ Keep sentences 5-15 words

**DON'T:**
- ✗ Use technical jargon
- ✗ Write very long or very short sentences
- ✗ Repeat the same phrases
- ✗ Use complex subordinate clauses
- ✗ Include stereotypical associations
- ✗ Use passive voice excessively
- ✗ Copy sentences from other sources

### Domain Selection

**Recommended Domains for Fongbe:**
1. **Family & Relationships**: Daily family interactions
2. **Health**: Basic health, hygiene, medical visits
3. **Education**: School, learning, teaching
4. **Commerce**: Shopping, markets, transactions
5. **Agriculture**: Farming, crops, livestock
6. **Food & Cooking**: Meals, recipes, ingredients
7. **Transportation**: Travel, vehicles, directions
8. **Work & Professions**: Jobs, workplace situations
9. **Community**: Social events, gatherings
10. **Nature & Environment**: Weather, seasons, landscape

**Sentences per Domain:**
- Minimum: 100 sentences
- Target: 150-200 sentences
- Maximum: 300 sentences (to avoid overrepresentation)

### Vocabulary Coverage Strategy

**Core Vocabulary (Priority 1):**
- Numbers (1-100)
- Time expressions (days, months, hours)
- Common verbs (be, have, go, do, make, etc.)
- Basic nouns (person, thing, place, time)
- Pronouns (I, you, he, she, we, they)
- Common adjectives (big, small, good, bad)
- Prepositions (in, on, at, to, from)

**Domain Vocabulary (Priority 2):**
- Domain-specific terms for each category
- Professional vocabulary
- Technical terms (when necessary)

**Extended Vocabulary (Priority 3):**
- Synonyms and variations
- Idiomatic expressions
- Cultural references

## Troubleshooting

### Installation Issues

**Problem**: `pip install` fails with permission error

**Solution**:
```bash
# Use virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# OR use --user flag
pip install --user -r requirements.txt
```

**Problem**: spaCy model download fails

**Solution**:
```bash
# Try direct download
python -m spacy download fr_core_news_md

# If that fails, download manually
pip install https://github.com/explosion/spacy-models/releases/download/fr_core_news_md-3.5.0/fr_core_news_md-3.5.0-py3-none-any.whl
```

**Problem**: `ModuleNotFoundError` after installation

**Solution**:
```bash
# Ensure package is installed
pip install -e .

# Verify installation
pip list | grep fongbe

# Check Python path
python -c "import sys; print(sys.path)"
```

### Data Loading Issues

**Problem**: "No CSV files found in input directory"

**Solution**:
- Verify directory path is correct
- Ensure files have `.csv` extension
- Check files are not empty
- Verify you have read permissions

**Problem**: "Unable to detect text column"

**Solution**:
- Rename column to one of: `sentence`, `text`, `phrase`, `content`
- Ensure column contains text data
- Check CSV is properly formatted

**Problem**: `UnicodeDecodeError` when loading CSV

**Solution**:
- Save CSV with UTF-8 encoding
- The pipeline auto-detects encoding, but UTF-8 is most reliable
- In Excel: Save As → CSV UTF-8

**Problem**: "Empty sentences detected"

**Solution**:
- Remove empty rows from CSV
- Check for rows with only whitespace
- Ensure each row has text content

### Analysis Issues

**Problem**: Analysis takes very long (>10 minutes)

**Solution**:
- Check dataset size (>10,000 sentences may be slow)
- Ensure sufficient RAM available
- Close other applications
- Consider processing in batches
- Check if spaCy model is loaded correctly

**Problem**: "Analyzer failed" error

**Solution**:
- Check error message for specific analyzer
- Verify configuration parameters are valid
- Ensure linguistic resources are available
- Try disabling problematic analyzer in config
- Check execution log for details

**Problem**: Metrics seem incorrect

**Solution**:
- Verify input data format is correct
- Check configuration thresholds
- Review sample sentences manually
- Compare with annotated CSV output
- Ensure domain extraction is working (check filenames)

### Dashboard Issues

**Problem**: Dashboard doesn't display properly

**Solution**:
- Open in modern browser (Chrome, Firefox, Safari, Edge)
- Check JavaScript is enabled
- Try different browser
- Verify HTML file is complete (not truncated)
- Check browser console for errors (F12)

**Problem**: Charts not showing

**Solution**:
- Ensure internet connection (Plotly CDN)
- Check browser console for errors
- Verify dashboard.html is complete
- Try refreshing page (Ctrl+F5)

**Problem**: Dashboard is slow/unresponsive

**Solution**:
- Large datasets (>5,000 sentences) may be slow
- Try closing other browser tabs
- Use Chrome for best performance
- Consider generating PDF report instead

### Configuration Issues

**Problem**: "Invalid configuration" error

**Solution**:
- Check YAML syntax (indentation, colons)
- Verify all required fields present
- Check data types (numbers, lists, strings)
- Compare with example_config.yaml
- Use YAML validator online

**Problem**: Custom configuration not being used

**Solution**:
- Verify --config flag is specified
- Check file path is correct
- Ensure file has .yaml or .yml extension
- Check file permissions (readable)

### Output Issues

**Problem**: Output directory not created

**Solution**:
- Check write permissions
- Verify parent directory exists
- Use absolute path
- Check disk space available

**Problem**: Some output files missing

**Solution**:
- Check execution log for errors
- Verify all analyzers completed successfully
- Check disk space
- Review terminal output for warnings

**Problem**: PDF generation fails

**Solution**:
- Ensure reportlab is installed: `pip install reportlab`
- Check write permissions
- Verify sufficient disk space
- Try generating other formats first

## Advanced Usage

### Batch Processing

Process multiple datasets:

```bash
#!/bin/bash
# process_all.sh

for dataset in dataset1 dataset2 dataset3; do
    echo "Processing $dataset..."
    fongbe-quality analyze \
        --input data/$dataset \
        --output results/$dataset \
        --config config/default_config.yaml
done
```

### Custom Analysis Scripts

Use the pipeline programmatically:

```python
from fongbe_quality.data.loader import DataLoader
from fongbe_quality.pipeline.controller import PipelineController
from fongbe_quality.config.loader import ConfigLoader

# Load configuration
config = ConfigLoader.load('config/my_config.yaml')

# Load data
loader = DataLoader()
sentences = loader.load_directory('data/sentences')

# Run pipeline
controller = PipelineController(config)
results = controller.run(sentences)

# Access results
print(f"TTR: {results.diversity.ttr}")
print(f"Avg length: {results.structural.word_distribution['mean']}")
```

### Filtering and Export

Filter sentences programmatically:

```python
import pandas as pd

# Load annotated results
df = pd.read_csv('results/annotated_sentences.csv')

# Filter high-quality sentences
high_quality = df[
    (df['quality_flag'] == 'OK') &
    (df['word_count'] >= 5) &
    (df['word_count'] <= 15) &
    (df['readability_score'] <= 60)
]

# Export filtered dataset
high_quality.to_csv('data/high_quality_sentences.csv', index=False)
```

### Integration with Other Tools

Export for annotation tools:

```python
import json

# Load results
with open('results/analysis_results.json', 'r') as f:
    results = json.load(f)

# Extract sentences needing review
needs_review = results['structural']['too_long'] + \
               results['structural']['too_short']

# Export for annotation tool
annotation_data = [
    {
        'text': s['text'],
        'issue': s['issue'],
        'suggestion': s['suggestion']
    }
    for s in needs_review
]

with open('for_annotation.json', 'w') as f:
    json.dump(annotation_data, f, indent=2)
```

## Frequently Asked Questions

**Q: How many sentences do I need?**
A: Minimum 500 for meaningful analysis, 1000+ recommended for model training.

**Q: Can I use this for languages other than French?**
A: Currently optimized for French. Adapting to other languages requires changing the spaCy model and linguistic resources.

**Q: How long does analysis take?**
A: ~1 minute for 1,000 sentences, ~5 minutes for 10,000 sentences (varies by hardware).

**Q: Can I disable certain analyzers?**
A: Yes, use the `enable_analyzers` configuration parameter.

**Q: What if my domain names have special characters?**
A: Use simple ASCII names for filenames. The pipeline extracts domain from filename.

**Q: Can I analyze data in batches?**
A: Yes, process separate directories and compare results across batches.

**Q: How do I update the reference vocabulary?**
A: Edit `src/fongbe_quality/resources/asr_reference_vocabulary.txt` (one word per line).

**Q: Can I export results to Excel?**
A: CSV files can be opened in Excel. For better formatting, use the PDF report.

**Q: What's the difference between annotated and filtered CSV?**
A: Annotated contains all sentences with scores. Filtered contains only problematic sentences.

**Q: How do I cite this tool?**
A: See the Citation section in README.md.

## Getting Help

**Documentation:**
- README.md - Quick start and overview
- This guide - Comprehensive usage instructions
- docs/best_practices.md - Data collection guidelines
- CLI_USAGE.md - Command reference

**Support Channels:**
- GitHub Issues: Report bugs and request features
- Email: your.email@example.com
- Documentation: docs/ directory

**Before Asking for Help:**
1. Check this guide and README
2. Review error messages carefully
3. Check execution log
4. Try with test data
5. Search existing GitHub issues

**When Reporting Issues:**
- Include error message
- Provide configuration file
- Describe steps to reproduce
- Include Python version and OS
- Attach execution log if possible

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Maintainer**: Fongbe Quality Pipeline Team
