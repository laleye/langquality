# Frequently Asked Questions (FAQ)

## General Questions

### What is LangQuality?

LangQuality is an open-source toolkit for analyzing text data quality for low-resource languages. It evaluates text across multiple dimensions (structure, linguistics, diversity, domain balance, gender bias) and provides actionable recommendations for improvement.

### Who should use LangQuality?

- **NLP Researchers** - Preparing datasets for model training
- **Linguists** - Analyzing corpus quality and balance
- **Data Collectors** - Ensuring high-quality text collection
- **ASR Developers** - Preparing text for speech recording
- **Translation Teams** - Validating parallel corpus quality

### What languages does LangQuality support?

LangQuality is language-agnostic and can work with any language through Language Packs. Currently available packs:

- **Fongbe** (fon) - Stable
- **French** (fra) - Stable
- **English** (eng) - Stable
- **Minangkabau** (min) - Minimal
- **Chuukese** (chk) - Experimental

You can create packs for additional languages. See the [Language Pack Guide](language_pack_guide.md).

### Is LangQuality free?

Yes! LangQuality is open-source software released under the MIT License. It's free to use, modify, and distribute.

## Installation & Setup

### How do I install LangQuality?

```bash
pip install langquality
```

See the [Installation Guide](user_guide/installation.md) for detailed instructions.

### What are the system requirements?

- Python 3.8 or higher
- 2GB RAM minimum (4GB recommended)
- 500MB disk space (more for language models)

### Do I need to install anything else?

Some language packs require additional dependencies:

```bash
# For French
python -m spacy download fr_core_news_md

# For English
python -m spacy download en_core_web_md
```

### I get "command not found: langquality"

The installation directory may not be in your PATH. Try:

```bash
# Use python -m
python -m langquality --help

# Or add to PATH (Linux/Mac)
export PATH="$HOME/.local/bin:$PATH"
```

### Can I use LangQuality without internet?

Yes, once installed. However, downloading spaCy models requires internet initially.

## Usage Questions

### What input formats are supported?

- **CSV** - Most common, auto-detects text column
- **JSON** - Structured data
- **JSONL** - JSON Lines format
- **TXT** - Plain text, one sentence per line

### How do I specify which column contains the text?

LangQuality auto-detects columns named: `text`, `sentence`, `phrase`, `content`, or any column with "text" in the name.

For custom column names, preprocess your CSV:

```bash
# Rename column
csvcut -c custom_column_name input.csv | csvformat -U 1 > output.csv
```

### Can I analyze multiple files at once?

Yes! Point to a directory:

```bash
langquality analyze -i data_directory/ -o results -l eng
```

### How long does analysis take?

- **Small datasets** (<1,000 sentences): <1 minute
- **Medium datasets** (1,000-10,000): 1-5 minutes
- **Large datasets** (>10,000): 5-30 minutes

Performance depends on:
- Number of sentences
- Enabled analyzers
- Language pack complexity
- System resources

### Can I run analysis in parallel?

Currently, LangQuality processes files sequentially. Parallel processing is planned for future versions.

Workaround:
```bash
# Split data and run multiple instances
split -l 1000 large_file.csv chunk_
langquality analyze -i chunk_aa -o results_aa -l eng &
langquality analyze -i chunk_ab -o results_ab -l eng &
```

## Language Packs

### How do I list available language packs?

```bash
langquality pack list
```

### How do I create a language pack for my language?

```bash
langquality pack create <language_code>
```

See the [Language Pack Guide](language_pack_guide.md) for detailed instructions.

### Can I use LangQuality without a language pack?

Yes, but with limited functionality. Create a minimal pack with just structural analysis:

```yaml
language:
  code: "xyz"
  name: "My Language"
  script: "Latin"
  direction: "ltr"

tokenization:
  method: "whitespace"

analyzers:
  enabled:
    - structural
    - diversity
```

### What if my language doesn't have linguistic resources?

Start with basic analyzers (structural, diversity) that don't require resources. Add resources incrementally as they become available.

### Can I modify an existing language pack?

Yes! Create a custom configuration that overrides specific settings:

```yaml
# my_config.yaml
thresholds:
  structural:
    min_words: 5  # Override default
```

Use it:
```bash
langquality analyze -i data.csv -o results -l eng -c my_config.yaml
```

## Analysis & Results

### What do the quality scores mean?

Each analyzer produces metrics with thresholds:

- ✅ **Good** - Meets quality targets
- ⚠️ **Warning** - Acceptable but could improve
- ❌ **Poor** - Below quality threshold

See [Analyzing Data](user_guide/analyzing_data.md) for detailed explanations.

### Why are some sentences flagged as "too short"?

Sentences with fewer than 3 words (default) are flagged because they:
- May lack context
- Are difficult to record clearly (for ASR)
- May not translate well
- Reduce dataset quality

Adjust the threshold if needed:
```yaml
thresholds:
  structural:
    min_words: 2  # More lenient
```

### What is Type-Token Ratio (TTR)?

TTR = (unique words) / (total words)

It measures vocabulary diversity:
- **High TTR** (>0.6) - Diverse vocabulary
- **Medium TTR** (0.4-0.6) - Moderate diversity
- **Low TTR** (<0.4) - Repetitive vocabulary

### How is readability calculated?

LangQuality uses the Flesch-Kincaid readability score:
- **Lower scores** - Easier to read
- **Higher scores** - More complex

Note: Designed for English, may not be accurate for other languages.

### What are "near-duplicates"?

Sentences that are very similar but not identical:
- "Hello, how are you?" 
- "Hello, how are you doing?"

They reduce dataset diversity and should be reviewed.

### Why is gender bias analysis important?

Gender-balanced datasets:
- Reduce model bias
- Represent diverse perspectives
- Improve fairness in NLP applications
- Meet ethical AI standards

### Can I disable specific analyzers?

Yes, in your configuration:

```yaml
analyzers:
  enabled:
    - structural
    - diversity
  disabled:
    - linguistic
    - gender_bias
```

Or use CLI (future feature):
```bash
langquality analyze -i data.csv -o results -l eng --disable gender_bias
```

## Output & Reporting

### Where are the results saved?

In the output directory you specify:

```bash
langquality analyze -i data.csv -o my_results -l eng
```

Results in `my_results/`:
- `dashboard.html` - Interactive visualization
- `analysis_results.json` - Detailed metrics
- `annotated_sentences.csv` - Sentences with scores
- `filtered_sentences.csv` - Rejected sentences
- `quality_report.pdf` - Summary report (optional)

### Can I customize the dashboard?

Not directly, but you can:
1. Use the JSON output for custom visualizations
2. Modify the HTML template (advanced)
3. Request features via GitHub issues

### How do I export results to Excel?

The CSV outputs can be opened in Excel directly. For JSON:

```python
import json
import pandas as pd

with open('analysis_results.json') as f:
    data = json.load(f)

df = pd.DataFrame(data['structural'])
df.to_excel('results.xlsx')
```

### Can I generate reports in other languages?

Currently, reports are in English. Internationalization is planned for future versions.

## Troubleshooting

### "No CSV files found in input directory"

Ensure:
- Directory contains `.csv` files
- Files have `.csv` extension (not `.CSV` or `.txt`)
- You have read permissions

### "Can't find model 'fr_core_news_md'"

Download the spaCy model:

```bash
python -m spacy download fr_core_news_md
```

### "UnicodeDecodeError" when loading data

LangQuality auto-detects encoding, but you can specify UTF-8 when creating CSVs:

```python
df.to_csv('output.csv', encoding='utf-8', index=False)
```

### Analysis is very slow

Optimize by:
- Disabling unused analyzers
- Using whitespace tokenization instead of spaCy
- Processing smaller batches
- Increasing system RAM

### Dashboard doesn't display charts

Ensure:
- Using a modern browser (Chrome, Firefox, Safari, Edge)
- JavaScript is enabled
- Opening the HTML file (not viewing source)

### "LanguagePackNotFoundError"

The specified language pack doesn't exist:

```bash
# List available packs
langquality pack list

# Check spelling of language code
langquality analyze -i data.csv -o results -l eng  # Not 'en'
```

## Advanced Usage

### Can I use LangQuality programmatically?

Yes! Import as a Python library:

```python
from langquality.pipeline.controller import PipelineController
from langquality.language_packs.manager import LanguagePackManager
from langquality.data.generic_loader import GenericDataLoader

# Load language pack
pack_manager = LanguagePackManager()
pack = pack_manager.load_language_pack('eng')

# Load data
loader = GenericDataLoader(pack)
sentences = loader.load_from_csv('data.csv')

# Run analysis
controller = PipelineController(pack)
results = controller.run(sentences)

# Access results
print(results.structural.avg_word_count)
```

### Can I create custom analyzers?

Yes! See the [Developer Guide](developer_guide/creating_analyzers.md).

### Can I integrate LangQuality into my pipeline?

Yes! Use it as a library or call via CLI in your scripts:

```bash
#!/bin/bash
# data_pipeline.sh

# Collect data
python collect_data.py

# Analyze quality
langquality analyze -i collected_data/ -o quality_check -l eng

# Check if quality is acceptable
python check_quality_threshold.py quality_check/analysis_results.json

# Continue pipeline if quality is good
if [ $? -eq 0 ]; then
    python continue_pipeline.py
fi
```

### Can I run LangQuality in Docker?

Yes! Create a Dockerfile:

```dockerfile
FROM python:3.10-slim

RUN pip install langquality
RUN python -m spacy download en_core_web_md

WORKDIR /data
ENTRYPOINT ["langquality"]
```

Build and run:
```bash
docker build -t langquality .
docker run -v $(pwd)/data:/data langquality analyze -i /data/input.csv -o /data/output -l eng
```

### Can I use LangQuality in Jupyter notebooks?

Yes!

```python
# Install in notebook
!pip install langquality

# Run analysis
!langquality analyze -i data.csv -o results -l eng

# Load results
import json
with open('results/analysis_results.json') as f:
    results = json.load(f)

# Visualize
import pandas as pd
df = pd.DataFrame(results['structural'])
df.plot()
```

## Contributing

### How can I contribute?

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines. Ways to contribute:

- Create language packs
- Report bugs
- Suggest features
- Improve documentation
- Submit code improvements

### I found a bug. What should I do?

1. Check if it's already reported: [GitHub Issues](https://github.com/langquality/langquality-toolkit/issues)
2. If not, create a new issue with:
   - Description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version)
   - Error messages/logs

### I have a feature request

Create a feature request issue on GitHub with:
- Description of the feature
- Use case / motivation
- Example of how it would work

### How do I submit a language pack?

1. Create the pack following the [Language Pack Guide](language_pack_guide.md)
2. Test thoroughly
3. Fork the repository
4. Add your pack to `src/langquality/language_packs/packs/`
5. Create a pull request

## Performance & Scalability

### What's the maximum dataset size?

LangQuality can handle:
- **Tested**: Up to 100,000 sentences
- **Theoretical**: Limited by available RAM

For very large datasets (>100K), consider:
- Processing in batches
- Disabling resource-intensive analyzers
- Using a machine with more RAM

### How much RAM do I need?

- **Small datasets** (<10K): 2GB
- **Medium datasets** (10K-50K): 4GB
- **Large datasets** (>50K): 8GB+

### Can I run LangQuality on a server?

Yes! It's designed for both local and server use:

```bash
# Run on server
nohup langquality analyze -i data.csv -o results -l eng > analysis.log 2>&1 &
```

### Does LangQuality support GPU acceleration?

Currently no. Most analyzers are CPU-bound. GPU support may be added for future ML-based analyzers.

## Licensing & Citation

### What license is LangQuality under?

MIT License - free for commercial and non-commercial use.

### How do I cite LangQuality?

```bibtex
@software{langquality,
  title={LangQuality: Language Quality Toolkit for Low-Resource Languages},
  author={LangQuality Contributors},
  year={2024},
  url={https://github.com/langquality/langquality-toolkit},
  version={1.0.0}
}
```

### Can I use LangQuality commercially?

Yes! The MIT License allows commercial use.

### Can I modify LangQuality?

Yes! You can modify and distribute modified versions under the MIT License terms.

## Getting Help

### Where can I get help?

- **Documentation**: [https://langquality.readthedocs.io](https://langquality.readthedocs.io)
- **GitHub Discussions**: [https://github.com/langquality/langquality-toolkit/discussions](https://github.com/langquality/langquality-toolkit/discussions)
- **GitHub Issues**: [https://github.com/langquality/langquality-toolkit/issues](https://github.com/langquality/langquality-toolkit/issues)
- **Email**: community@langquality.org

### How do I report a security issue?

Email security@langquality.org with details. Do not create public issues for security vulnerabilities.

### Is there a community forum?

Yes! Use [GitHub Discussions](https://github.com/langquality/langquality-toolkit/discussions) for:
- Questions
- Ideas
- Show and tell
- Language pack announcements

## Still Have Questions?

If your question isn't answered here:

1. Check the [User Guide](user_guide/)
2. Search [GitHub Discussions](https://github.com/langquality/langquality-toolkit/discussions)
3. Ask a new question in Discussions
4. Contact us at community@langquality.org
