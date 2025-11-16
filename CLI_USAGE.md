# CLI Usage Reference

Complete command-line interface reference for LangQuality - Language Quality Toolkit for Low-Resource Languages.

## Table of Contents

- [Installation](#installation)
- [Basic Usage](#basic-usage)
- [Command Reference](#command-reference)
- [Language Pack Commands](#language-pack-commands)
- [Options](#options)
- [Examples](#examples)
- [Exit Codes](#exit-codes)
- [Environment Variables](#environment-variables)

## Installation

After installing the package, the `langquality` command becomes available:

```bash
pip install -e .
```

Verify installation:

```bash
langquality --version
```

## Basic Usage

The basic command structure is:

```bash
langquality analyze --language <code> [OPTIONS]
```

Minimum required options:
- `--language` or `-l`: Language pack code (ISO 639-3, e.g., fon, eng, fra)
- `--input` or `-i`: Input directory with data files
- `--output` or `-o`: Output directory for results

Example:

```bash
langquality analyze --language fon --input data/sentences --output results
```

You can also run without a language pack (language-agnostic mode):

```bash
langquality analyze --input data/sentences --output results
```

## Command Reference

### Main Command: `langquality`

The root command provides access to all pipeline functionality.

```bash
langquality [OPTIONS] COMMAND [ARGS]...
```

**Options:**
- `--version`: Show version and exit
- `--help`: Show help message and exit

**Commands:**
- `analyze`: Run quality analysis pipeline
- `pack`: Manage language packs

### Subcommand: `analyze`

Run the complete quality analysis pipeline.

```bash
langquality analyze [OPTIONS]
```

## Language Pack Commands

### List Available Packs

List all installed language packs:

```bash
langquality pack list
```

### Get Pack Information

Show detailed information about a specific language pack:

```bash
langquality pack info <language_code>
```

Example:
```bash
langquality pack info fon
```

### Create New Pack

Create a new language pack template:

```bash
langquality pack create <language_code> --name "<Language Name>" [OPTIONS]
```

**Options:**
- `--name` or `-n`: Full language name (required)
- `--output` or `-o`: Output directory (default: current directory)
- `--author`: Pack author name
- `--email`: Author email
- `--minimal`: Create minimal template (only required files)

Example:
```bash
langquality pack create xyz --name "My Language" --author "John Doe" --email "john@example.com"
```

### Validate Pack

Validate a language pack structure and content:

```bash
langquality pack validate <pack_path> [OPTIONS]
```

**Options:**
- `--verbose` or `-v`: Show detailed validation information

Example:
```bash
langquality pack validate path/to/language_pack --verbose
```

## Options

### Required Options

#### `--language CODE` or `-l CODE`

Language pack code (ISO 639-3) to use for analysis.

- **Type**: String (3-letter language code)
- **Required**: No (but recommended)
- **Example**: `--language fon`
- **Notes**: 
  - Use ISO 639-3 codes (e.g., fon, eng, fra)
  - If not specified, runs in language-agnostic mode
  - Use `langquality pack list` to see available packs

#### `--input PATH` or `-i PATH`

Path to directory containing data files to analyze.

- **Type**: Directory path (string)
- **Required**: Yes
- **Example**: `--input data/sentences`
- **Notes**: 
  - Directory must exist
  - Supports CSV, JSON, and TXT files
  - Can be relative or absolute path

#### `--output PATH` or `-o PATH`

Path to directory where analysis results will be saved.

- **Type**: Directory path (string)
- **Required**: Yes
- **Example**: `--output results/analysis_2024`
- **Notes**:
  - Directory will be created if it doesn't exist
  - Existing files may be overwritten
  - Can be relative or absolute path

### Optional Options

#### `--config PATH` or `-c PATH`

Path to custom YAML configuration file.

- **Type**: File path (string)
- **Required**: No
- **Default**: Uses language pack configuration or built-in defaults
- **Example**: `--config config/my_settings.yaml`
- **Notes**:
  - File must be valid YAML format
  - See `config/example_config.yaml` for structure
  - Overrides language pack configuration if specified
  - Invalid config will cause error at startup

#### `--verbose` or `-v`

Enable verbose output with detailed progress information.

- **Type**: Flag (boolean)
- **Required**: No
- **Default**: False
- **Example**: `--verbose`
- **Notes**:
  - Shows detailed progress for each analyzer
  - Useful for debugging
  - Cannot be used with `--quiet`

#### `--quiet` or `-q`

Suppress all output except errors.

- **Type**: Flag (boolean)
- **Required**: No
- **Default**: False
- **Example**: `--quiet`
- **Notes**:
  - Only critical errors are displayed
  - Useful for automated scripts
  - Cannot be used with `--verbose`

#### `--help`

Show help message and exit.

- **Type**: Flag (boolean)
- **Example**: `--help`

## Examples

### Basic Analysis

Analyze sentences with Fongbe language pack:

```bash
langquality analyze --language fon --input data/sentences --output results
```

### Language-Agnostic Mode

Analyze without a specific language pack:

```bash
langquality analyze --input data/sentences --output results
```

### Custom Configuration

Use custom thresholds and settings:

```bash
langquality analyze \
  --language fon \
  --input data/sentences \
  --output results \
  --config config/strict_quality.yaml
```

### Working with Language Packs

List available language packs:

```bash
langquality pack list
```

Get information about a pack:

```bash
langquality pack info fon
```

Create a new language pack:

```bash
langquality pack create xyz --name "My Language" --author "Your Name"
```

Validate a language pack:

```bash
langquality pack validate path/to/pack
```

### Verbose Mode

See detailed progress information:

```bash
langquality analyze \
  --language fon \
  --input data/sentences \
  --output results \
  --verbose
```


### Quiet Mode

Run silently (for scripts):

```bash
langquality analyze \
  --language fon \
  --input data/sentences \
  --output results \
  --quiet
```

### Absolute Paths

Use full paths for clarity:

```bash
langquality analyze \
  --language fon \
  --input /home/user/project/data/sentences \
  --output /home/user/project/results/2024-01-15
```

### Test Data

Run on test dataset:

```bash
langquality analyze \
  --language fon \
  --input tests/data/small_dataset \
  --output test_results
```

### Multiple Runs with Different Configs

Compare results with different configurations:

```bash
# Strict quality standards
langquality analyze \
  --language fon \
  -i data/sentences \
  -o results/strict \
  -c config/strict.yaml

# Relaxed standards
langquality analyze \
  --language fon \
  -i data/sentences \
  -o results/relaxed \
  -c config/relaxed.yaml

# Default standards
langquality analyze \
  --language fon \
  -i data/sentences \
  -o results/default
```

### Multiple Languages

Analyze the same data with different language packs:

```bash
# Analyze with Fongbe pack
langquality analyze --language fon -i data/ -o results/fon

# Analyze with French pack
langquality analyze --language fra -i data/ -o results/fra

# Analyze with English pack
langquality analyze --language eng -i data/ -o results/eng
```

### Batch Processing Script

Process multiple datasets:

```bash
#!/bin/bash
# analyze_all.sh

datasets=("dataset1" "dataset2" "dataset3")

for dataset in "${datasets[@]}"; do
    echo "Analyzing $dataset..."
    langquality analyze \
        --language fon \
        --input "data/$dataset" \
        --output "results/$dataset" \
        --config "config/default_config.yaml" \
        --quiet
    
    if [ $? -eq 0 ]; then
        echo "✓ $dataset completed successfully"
    else
        echo "✗ $dataset failed"
    fi
done
```

### With Error Handling

Robust script with error checking:

```bash
#!/bin/bash

LANGUAGE="fon"
INPUT_DIR="data/sentences"
OUTPUT_DIR="results/$(date +%Y%m%d_%H%M%S)"
CONFIG_FILE="config/default_config.yaml"

# Check if input directory exists
if [ ! -d "$INPUT_DIR" ]; then
    echo "Error: Input directory not found: $INPUT_DIR"
    exit 1
fi

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Config file not found: $CONFIG_FILE"
    exit 1
fi

# Check if language pack exists
if ! langquality pack info "$LANGUAGE" > /dev/null 2>&1; then
    echo "Error: Language pack not found: $LANGUAGE"
    echo "Available packs:"
    langquality pack list
    exit 1
fi

# Run analysis
echo "Starting analysis..."
langquality analyze \
    --language "$LANGUAGE" \
    --input "$INPUT_DIR" \
    --output "$OUTPUT_DIR" \
    --config "$CONFIG_FILE" \
    --verbose

# Check exit code
if [ $? -eq 0 ]; then
    echo "Analysis completed successfully!"
    echo "Results saved to: $OUTPUT_DIR"
    echo "Open dashboard: $OUTPUT_DIR/dashboard.html"
else
    echo "Analysis failed!"
    exit 1
fi
```

## Exit Codes

The CLI uses standard exit codes:

- **0**: Success - Analysis completed without errors
- **1**: General error - Analysis failed or invalid arguments
- **2**: Configuration error - Invalid or missing configuration
- **3**: Data error - Input data not found or invalid format

### Checking Exit Codes

In bash scripts:

```bash
langquality analyze -i data -o results

if [ $? -eq 0 ]; then
    echo "Success"
else
    echo "Failed with exit code: $?"
fi
```

In Python scripts:

```python
import subprocess

result = subprocess.run([
    'langquality', 'analyze',
    '--input', 'data',
    '--output', 'results'
])

if result.returncode == 0:
    print("Success")
else:
    print(f"Failed with exit code: {result.returncode}")
```

## Environment Variables

### FONGBE_CONFIG_PATH

Default configuration file path.

```bash
export FONGBE_CONFIG_PATH=/path/to/config.yaml
langquality analyze -i data -o results
# Will use config from FONGBE_CONFIG_PATH if --config not specified
```

### FONGBE_LOG_LEVEL

Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).

```bash
export FONGBE_LOG_LEVEL=DEBUG
langquality analyze -i data -o results --verbose
```

### FONGBE_RESOURCES_PATH

Override default resources directory.

```bash
export FONGBE_RESOURCES_PATH=/custom/resources
langquality analyze -i data -o results
```

## Output Files

After successful execution, the output directory contains:

```
results/
├── dashboard.html              # Interactive visualization
├── analysis_results.json       # Complete metrics (JSON)
├── annotated_sentences.csv     # All sentences with scores
├── filtered_sentences.csv      # Problematic sentences only
├── report.pdf                  # Summary report
└── execution_log.txt           # Execution log
```

### Opening the Dashboard

**Linux/macOS:**
```bash
open results/dashboard.html
# or
xdg-open results/dashboard.html
```

**Windows:**
```bash
start results/dashboard.html
```

**From Python:**
```python
import webbrowser
webbrowser.open('results/dashboard.html')
```

## Common Issues

### "No CSV files found"

**Problem**: Input directory doesn't contain CSV files

**Solution**:
```bash
# Check directory contents
ls -la data/sentences/

# Ensure files have .csv extension
# Ensure you have read permissions
```

### "Permission denied"

**Problem**: No write permission for output directory

**Solution**:
```bash
# Check permissions
ls -ld results/

# Create directory with proper permissions
mkdir -p results
chmod 755 results
```

### "Configuration error"

**Problem**: Invalid YAML configuration

**Solution**:
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('config/my_config.yaml'))"

# Compare with example
diff config/my_config.yaml config/example_config.yaml
```

### "spaCy model not found"

**Problem**: French language model not installed

**Solution**:
```bash
python -m spacy download fr_core_news_md
```

## Advanced Usage

### Programmatic Access

Use the CLI from Python code:

```python
import subprocess
import json

# Run analysis
result = subprocess.run([
    'langquality', 'analyze',
    '--language', 'fon',
    '--input', 'data/sentences',
    '--output', 'results',
    '--quiet'
], capture_output=True, text=True)

if result.returncode == 0:
    # Load results
    with open('results/analysis_results.json') as f:
        analysis = json.load(f)
    
    print(f"TTR: {analysis['diversity']['ttr']}")
    print(f"Total sentences: {analysis['structural']['total_sentences']}")
else:
    print(f"Error: {result.stderr}")
```

### Managing Language Packs Programmatically

```python
import subprocess
import json

# List available packs
result = subprocess.run(['langquality', 'pack', 'list'], 
                       capture_output=True, text=True)
print(result.stdout)

# Get pack info
result = subprocess.run(['langquality', 'pack', 'info', 'fon'],
                       capture_output=True, text=True)
print(result.stdout)

# Create a new pack
result = subprocess.run([
    'langquality', 'pack', 'create', 'xyz',
    '--name', 'My Language',
    '--output', 'packs/',
    '--author', 'Your Name'
], capture_output=True, text=True)

if result.returncode == 0:
    print("Pack created successfully!")
```

### Integration with Make

Create a Makefile:

```makefile
.PHONY: analyze clean test list-packs

LANGUAGE ?= fon

analyze:
	langquality analyze \
		--language $(LANGUAGE) \
		--input data/sentences \
		--output results \
		--config config/default_config.yaml

test:
	langquality analyze \
		--language $(LANGUAGE) \
		--input tests/data/small_dataset \
		--output test_results

list-packs:
	langquality pack list

pack-info:
	langquality pack info $(LANGUAGE)

clean:
	rm -rf results/ test_results/

dashboard:
	open results/dashboard.html
```

Usage:
```bash
make analyze
make analyze LANGUAGE=fra
make list-packs
make pack-info LANGUAGE=fon
make dashboard
make clean
```

### CI/CD Integration

GitHub Actions example:

```yaml
name: Data Quality Check

on: [push, pull_request]

jobs:
  quality-check:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        language: [fon, fra, eng]
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          python -m spacy download fr_core_news_md
          pip install -e .
      
      - name: List available language packs
        run: langquality pack list
      
      - name: Run quality analysis
        run: |
          langquality analyze \
            --language ${{ matrix.language }} \
            --input data/sentences \
            --output results/${{ matrix.language }} \
            --quiet
      
      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: quality-results-${{ matrix.language }}
          path: results/${{ matrix.language }}/
```

## Getting Help

### Command Help

```bash
# General help
langquality --help

# Command-specific help
langquality analyze --help
langquality pack --help
langquality pack list --help
langquality pack create --help
```

### Documentation

- **User Guide**: `docs/user_guide.md`
- **Best Practices**: `docs/best_practices.md`
- **README**: `README.md`

### Support

- **GitHub Issues**: Report bugs and request features
- **Email**: your.email@example.com

---

**Version**: 1.0.0  
**Last Updated**: November 2025  
**Maintainer**: LangQuality Community
