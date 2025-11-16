# Configuration Guide

This guide provides detailed information about all configuration parameters in the Fongbe Data Quality Pipeline.

## Table of Contents

1. [Configuration File Structure](#configuration-file-structure)
2. [Analysis Parameters](#analysis-parameters)
3. [Pipeline Configuration](#pipeline-configuration)
4. [Output Configuration](#output-configuration)
5. [Logging Configuration](#logging-configuration)
6. [Use Case Examples](#use-case-examples)
7. [Best Practices](#best-practices)

## Configuration File Structure

The configuration file uses YAML format with the following main sections:

```yaml
analysis:      # Quality analysis thresholds and parameters
pipeline:      # Input/output paths and analyzer selection
outputs:       # Output format configuration
logging:       # Logging verbosity and destination
```

## Analysis Parameters

### Sentence Length Constraints

Controls acceptable sentence length ranges for quality assessment.

```yaml
analysis:
  min_words: 3      # Minimum words per sentence
  max_words: 20     # Maximum words per sentence
```

**Purpose**: Ensure sentences are appropriate for speech recording and translation.

**Guidelines**:
- **ASR Training**: 3-20 words (clear pronunciation, manageable length)
- **Speech Translation**: 5-15 words (optimal for translation quality)
- **Conversational**: 2-25 words (natural speech patterns)

**Impact**:
- Too short: Lack context, difficult to translate accurately
- Too long: Hard to pronounce, increased recording errors

### Readability Scores

Measures text complexity using Flesch-Kincaid readability formula.

```yaml
analysis:
  min_readability_score: 0      # Minimum acceptable score
  max_readability_score: 60     # Maximum acceptable score
```

**Score Interpretation**:
- **90-100**: Very easy (5th grade level)
- **60-70**: Standard (8th-9th grade level)
- **30-50**: Difficult (college level)
- **0-30**: Very difficult (graduate level)

**Guidelines**:
- **General Audience**: max = 60 (standard readability)
- **Educational Content**: max = 50 (controlled complexity)
- **Technical Content**: max = 70 (allows some complexity)

**Formula**: Based on average sentence length and syllables per word.

### Vocabulary Diversity

Measures lexical richness using Type-Token Ratio (TTR).

```yaml
analysis:
  target_ttr: 0.65    # Target Type-Token Ratio
```

**Calculation**: TTR = (unique words) / (total words)

**Interpretation**:
- **0.4-0.5**: Low diversity (repetitive vocabulary)
- **0.5-0.7**: Good diversity (recommended range)
- **0.7-0.9**: High diversity (very varied vocabulary)

**Guidelines**:
- **Conversational**: 0.55 (natural repetition)
- **Educational**: 0.65 (balanced variety)
- **Literary**: 0.75 (rich vocabulary)

**Note**: TTR naturally decreases with larger datasets. For datasets > 10,000 words, consider using MATTR (Moving Average TTR) instead.

### Domain Balance

Ensures balanced representation across thematic domains.

```yaml
analysis:
  min_domain_representation: 0.10    # 10% minimum per domain
  max_domain_representation: 0.30    # 30% maximum per domain
```

**Purpose**: Prevent over-representation of specific topics.

**Calculation**: domain_percentage = (domain_sentences) / (total_sentences)

**Guidelines**:
- **Balanced Dataset**: min=0.10, max=0.30 (even distribution)
- **Flexible Dataset**: min=0.05, max=0.40 (some variation allowed)
- **Focused Dataset**: min=0.02, max=0.50 (concentrated on key domains)

**Example**: With 5 domains
- Ideal: 20% per domain
- Acceptable: 10-30% per domain
- Warning: <10% (underrepresented) or >30% (overrepresented)

### Gender Bias Thresholds

Defines acceptable range for gender representation.

```yaml
analysis:
  target_gender_ratio:
    - 0.45    # Minimum acceptable ratio (45%)
    - 0.55    # Maximum acceptable ratio (55%)
```

**Calculation**: ratio = feminine_mentions / (masculine_mentions + feminine_mentions)

**Interpretation**:
- **0.50**: Perfect balance (50% feminine, 50% masculine)
- **0.45-0.55**: Acceptable range (within 5% of balance)
- **<0.40 or >0.60**: Significant bias detected

**Guidelines**:
- **Strict Balance**: [0.45, 0.55] (±5% tolerance)
- **Moderate Balance**: [0.40, 0.60] (±10% tolerance)
- **Flexible**: [0.35, 0.65] (±15% tolerance)

**Detection**: Counts gendered pronouns, articles, nouns, and profession terms.

### Custom Jargon Terms

List of technical terms to flag during analysis.

```yaml
analysis:
  jargon_terms:
    - "algorithme"
    - "infrastructure"
    - "méthodologie"
```

**Purpose**: Identify specialized vocabulary that may be:
- Difficult to translate
- Hard to pronounce
- Not understood by general audience

**Usage**:
- Add domain-specific technical terms
- Include abbreviations and acronyms
- List words with no direct translation in target language

**Impact**: Sentences containing jargon terms are flagged in reports.

### Reference Vocabulary

Path to vocabulary file for coverage analysis.

```yaml
analysis:
  reference_vocabulary: "path/to/vocabulary.txt"
```

**Purpose**: Measure how well your dataset covers essential vocabulary.

**File Format**: One word per line (UTF-8 encoding)
```
le
de
un
être
avoir
...
```

**Options**:
- Use provided French frequency lexicon (5000 most common words)
- Create custom vocabulary for your domain
- Set to `null` to skip coverage analysis

**Metric**: coverage = (words_in_dataset ∩ reference_vocab) / reference_vocab

## Pipeline Configuration

### Input/Output Paths

Specify data locations.

```yaml
pipeline:
  input_directory: "data/input"
  output_directory: "data/output"
```

**Input Directory**:
- Should contain CSV files with columns: `fongbe,french`
- File names determine domain (e.g., `education.csv` → "education" domain)
- Can contain subdirectories (processed recursively)

**Output Directory**:
- Created automatically if doesn't exist
- Contains all generated reports and exports
- Organized by timestamp for multiple runs

### Analyzer Selection

Choose which analyzers to run.

```yaml
pipeline:
  enable_analyzers:
    - structural
    - linguistic
    - diversity
    - domain
    - gender_bias
```

**Available Analyzers**:

1. **structural**: Sentence length and structure
   - Length distributions
   - Outlier detection
   - Statistical metrics

2. **linguistic**: Readability and complexity
   - Flesch-Kincaid scores
   - Lexical complexity
   - Syntactic complexity
   - Jargon detection

3. **diversity**: Vocabulary and structural variety
   - Type-Token Ratio
   - N-gram analysis
   - Duplicate detection
   - Vocabulary coverage

4. **domain**: Thematic distribution
   - Domain counts and percentages
   - Balance analysis
   - Under/over-representation

5. **gender_bias**: Gender representation
   - Gender mention counts
   - Ratio calculation
   - Stereotype detection
   - Bias scoring

**Options**:
```yaml
# Enable all analyzers
enable_analyzers: ["all"]

# Enable specific analyzers
enable_analyzers: ["structural", "domain"]

# Enable all except one
enable_analyzers: ["all", "!gender_bias"]
```

### Language

Specify the source language.

```yaml
pipeline:
  language: "fr"
```

**Currently Supported**: French (`fr`)

**Future Support**: Additional languages can be added by:
- Providing language-specific resources
- Adapting readability formulas
- Updating linguistic analyzers

## Output Configuration

Control which outputs are generated.

```yaml
outputs:
  generate_dashboard: true    # Interactive HTML dashboard
  export_json: true          # Detailed metrics in JSON
  export_csv: true           # Annotated CSV with scores
  export_pdf: false          # PDF report (optional)
  create_log: true           # Execution log
```

### Output Types

**Dashboard** (`dashboard.html`):
- Interactive visualizations
- All metrics and charts
- Recommendations section
- Best for: Human review and presentation

**JSON** (`results.json`):
- Complete metrics data
- Machine-readable format
- Includes all analyzer outputs
- Best for: Programmatic access, archiving

**Annotated CSV** (`annotated.csv`):
- Original sentences with quality scores
- Per-sentence metrics
- Filterable in spreadsheet software
- Best for: Manual review, filtering

**Filtered CSV** (`filtered_sentences.csv`):
- Sentences that failed quality checks
- Includes rejection reasons
- Best for: Identifying problematic data

**PDF Report** (`report.pdf`):
- Professional formatted report
- Key visualizations and metrics
- Executive summary
- Best for: Sharing with stakeholders

**Execution Log** (`execution_log.txt`):
- Timestamp and configuration
- Summary statistics
- Warnings and errors
- Best for: Debugging, audit trail

## Logging Configuration

Control logging verbosity and destination.

```yaml
logging:
  level: "INFO"              # Logging level
  log_file: "pipeline.log"   # Log file path
```

### Logging Levels

**DEBUG**:
- Very detailed information
- Function entry/exit
- Variable values
- Use for: Troubleshooting, development

**INFO** (recommended):
- General progress information
- Major steps completed
- Summary statistics
- Use for: Normal operation

**WARNING**:
- Warning messages only
- Potential issues
- Degraded functionality
- Use for: Production monitoring

**ERROR**:
- Error messages only
- Failed operations
- Use for: Error tracking

**CRITICAL**:
- Critical errors only
- System failures
- Use for: Minimal logging

### Log File

```yaml
log_file: "pipeline.log"    # Relative to output directory
log_file: null              # Disable file logging (console only)
```

## Use Case Examples

### ASR Training Data

Optimize for speech recognition model training.

```yaml
analysis:
  min_words: 3
  max_words: 20
  max_readability_score: 60
  target_ttr: 0.60
  min_domain_representation: 0.15
  max_domain_representation: 0.25

pipeline:
  enable_analyzers: ["all"]

outputs:
  generate_dashboard: true
  export_csv: true
  export_pdf: true
```

**Characteristics**:
- Clear, pronounceable sentences
- Moderate length for recording
- Balanced domain coverage
- Good vocabulary diversity

### Conversational Data

Natural language for dialogue systems.

```yaml
analysis:
  min_words: 2
  max_words: 25
  max_readability_score: 70
  target_ttr: 0.55
  min_domain_representation: 0.05
  max_domain_representation: 0.40

pipeline:
  enable_analyzers: ["structural", "diversity", "domain"]

outputs:
  generate_dashboard: true
  export_json: true
```

**Characteristics**:
- Variable sentence length
- Natural repetition patterns
- Flexible domain distribution
- Conversational vocabulary

### Educational Content

Structured learning materials.

```yaml
analysis:
  min_words: 5
  max_words: 15
  max_readability_score: 50
  target_ttr: 0.70
  min_domain_representation: 0.10
  max_domain_representation: 0.30

pipeline:
  enable_analyzers: ["all"]

outputs:
  generate_dashboard: true
  export_csv: true
  export_pdf: true
```

**Characteristics**:
- Controlled complexity
- Rich vocabulary
- Balanced topics
- Educational appropriateness

### Quick Analysis

Fast analysis with essential metrics only.

```yaml
pipeline:
  enable_analyzers: ["structural", "domain"]

outputs:
  generate_dashboard: true
  export_json: false
  export_csv: false
  export_pdf: false

logging:
  level: "WARNING"
```

**Characteristics**:
- Minimal analyzers
- Fast execution
- Essential metrics only
- Reduced output

## Best Practices

### 1. Start with Default Configuration

Begin with `config/default_config.yaml` and adjust based on results.

### 2. Iterate on Thresholds

Run analysis → Review results → Adjust thresholds → Re-run

### 3. Document Custom Configurations

Add comments explaining why you chose specific values.

```yaml
# Increased max_words to 25 because our domain (legal text)
# naturally has longer sentences
max_words: 25
```

### 4. Version Control Configurations

Keep configuration files in version control to track changes.

### 5. Use Separate Configs for Different Stages

```
config/
  ├── development.yaml    # Relaxed thresholds for testing
  ├── staging.yaml        # Moderate thresholds for review
  └── production.yaml     # Strict thresholds for final data
```

### 6. Validate Configuration

The pipeline validates configuration on startup. Check logs for warnings.

### 7. Profile Before Optimizing

Use `profile_performance.py` to identify actual bottlenecks before disabling analyzers.

### 8. Balance Quality and Quantity

Stricter thresholds = higher quality but fewer sentences
Relaxed thresholds = more sentences but variable quality

### 9. Consider Your Use Case

ASR training needs different quality criteria than conversational data.

### 10. Monitor Trends Over Time

Track metrics across multiple data collection rounds to ensure consistency.

## Troubleshooting

### Configuration Not Loading

**Error**: `ConfigurationError: Invalid configuration file`

**Solutions**:
- Check YAML syntax (indentation, colons, dashes)
- Validate with online YAML validator
- Ensure file encoding is UTF-8

### Unexpected Metric Values

**Issue**: Metrics seem incorrect or out of range

**Solutions**:
- Run `validate_real_data.py` to check metric calculations
- Verify input data format (CSV structure)
- Check for encoding issues in text
- Review threshold values for typos

### Performance Issues

**Issue**: Analysis takes too long

**Solutions**:
- Disable unused analyzers
- Reduce logging level to WARNING
- Disable PDF generation
- Profile with `profile_performance.py`

### Missing Outputs

**Issue**: Expected output files not generated

**Solutions**:
- Check `outputs` section in config
- Verify output directory permissions
- Review logs for errors
- Ensure all dependencies installed

## Reference

### Complete Configuration Template

```yaml
analysis:
  min_words: 3
  max_words: 20
  min_readability_score: 0
  max_readability_score: 60
  target_ttr: 0.65
  min_domain_representation: 0.10
  max_domain_representation: 0.30
  target_gender_ratio: [0.45, 0.55]
  jargon_terms: []
  reference_vocabulary: null

pipeline:
  input_directory: "data/input"
  output_directory: "data/output"
  enable_analyzers: ["all"]
  language: "fr"

outputs:
  generate_dashboard: true
  export_json: true
  export_csv: true
  export_pdf: false
  create_log: true

logging:
  level: "INFO"
  log_file: "pipeline.log"
```

### Parameter Quick Reference

| Parameter | Type | Default | Range | Purpose |
|-----------|------|---------|-------|---------|
| min_words | int | 3 | 1-100 | Minimum sentence length |
| max_words | int | 20 | 1-100 | Maximum sentence length |
| max_readability_score | float | 60 | 0-100 | Maximum complexity |
| target_ttr | float | 0.65 | 0-1 | Target vocabulary diversity |
| min_domain_representation | float | 0.10 | 0-1 | Minimum domain percentage |
| max_domain_representation | float | 0.30 | 0-1 | Maximum domain percentage |
| target_gender_ratio | list | [0.45, 0.55] | [0-1, 0-1] | Acceptable gender ratio range |

---

For more information, see:
- [User Guide](user_guide.md)
- [Best Practices](best_practices.md)
- [Testing Guide](../TESTING.md)
