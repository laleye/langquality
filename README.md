# LangQuality - Language Quality Toolkit for Low-Resource Languages

[![PyPI version](https://badge.fury.io/py/langquality.svg)](https://badge.fury.io/py/langquality)
[![CI Status](https://github.com/laleye/langquality/workflows/CI/badge.svg)](https://github.com/langquality/langquality/actions)
[![Coverage](https://codecov.io/gh/laleye/langquality/branch/main/graph/badge.svg)](https://codecov.io/gh/laleye/langquality)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Documentation](https://readthedocs.org/projects/langquality/badge/?version=latest)](https://langquality.readthedocs.io/)

A modular, extensible Python toolkit for analyzing the quality of text and audio datasets for low-resource languages. LangQuality helps researchers and developers ensure high-quality datasets for training NLP models (ASR, machine translation, language models) across diverse languages.

## ✨ Key Features

### 🌍 Multi-Language Support via Language Packs
- **Language-agnostic architecture**: Works with any language through configurable Language Packs
- **Pre-built packs**: Fongbe, French, English, and more
- **Easy customization**: Create your own Language Pack in minutes
- **Community-driven**: Share and discover Language Packs from the community

### 🔍 Comprehensive Quality Analysis
- **Structural Analysis**: Sentence length distribution, outlier detection, statistical metrics
- **Linguistic Analysis**: Readability scores, lexical complexity, morphological features
- **Diversity Analysis**: Vocabulary richness (TTR), n-gram distributions, duplicate detection
- **Domain Analysis**: Thematic balance, under/over-represented categories
- **Gender Bias Detection**: Gender representation, stereotype detection, balance metrics

### 🔌 Extensible Plugin System
- **Custom analyzers**: Add your own analysis modules without modifying core code
- **Automatic discovery**: Drop plugins into a directory and they're automatically loaded
- **Language-specific analyzers**: Create analyzers tailored to specific languages

### 📊 Rich Output Formats
- **Interactive Dashboard**: Beautiful HTML visualizations with Plotly
- **Actionable Recommendations**: Prioritized suggestions based on best practices
- **Multiple Exports**: JSON, CSV, PDF reports, execution logs
- **Per-sentence annotations**: Quality scores and flags for each sentence

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI
pip install langquality

# Install with all optional dependencies
pip install langquality[all]

# Download language models (if using spaCy-based packs)
python -m spacy download fr_core_news_md  # For French
python -m spacy download en_core_web_md   # For English
```

### Basic Usage

Analyze a dataset with a specific language:

```bash
# Analyze Fongbe data
langquality analyze --input data/fongbe_sentences --output results --language fon

# Analyze French data
langquality analyze --input data/french_sentences --output results --language fra

# Analyze English data
langquality analyze --input data/english_sentences --output results --language eng
```

### View Results

```bash
# Open the interactive dashboard
open results/dashboard.html
```

### Python API

```python
from langquality.pipeline import PipelineController
from langquality.language_packs import LanguagePackManager
from langquality.data import GenericDataLoader

# Load a language pack
pack_manager = LanguagePackManager()
language_pack = pack_manager.load_language_pack("fon")

# Load your data
loader = GenericDataLoader(language_pack)
sentences = loader.load_from_csv("data/sentences.csv")

# Run analysis
controller = PipelineController(language_pack)
results = controller.run(sentences)

# Access results
print(f"Total sentences: {results.structural.total_sentences}")
print(f"Average readability: {results.linguistic.avg_readability_score}")
```

## 📦 Language Packs

Language Packs are self-contained configurations that adapt LangQuality to specific languages. Each pack includes:
- Language-specific configuration (tokenization, thresholds, etc.)
- Linguistic resources (lexicons, stopwords, gender terms, etc.)
- Optional custom analyzers

### Available Language Packs

| Language | Code | Status | Resources |
|----------|------|--------|-----------|
| **Fongbe** | `fon` | ✅ Stable | Full (lexicon, gender terms, ASR vocabulary) |
| **French** | `fra` | ✅ Stable | Full (lexicon, stopwords, gender terms, professions) |
| **English** | `eng` | ✅ Stable | Full (lexicon, stopwords, gender terms, professions) |
| **Minangkabau** | `min` | 🚧 Minimal | Basic configuration only |
| **Your Language** | `xxx` | 💡 Create one! | See [Language Pack Guide](docs/language_pack_guide.md) |

### Managing Language Packs

```bash
# List installed packs
langquality pack list

# Show pack details
langquality pack info fon

# Create a new pack template
langquality pack create <language_code>

# Validate a pack
langquality pack validate path/to/pack
```

### Creating Your Own Language Pack

Creating a Language Pack for your language is straightforward:

1. **Generate a template**:
   ```bash
   langquality pack create <your_language_code>
   ```

2. **Configure the pack**: Edit `config.yaml` with language-specific settings

3. **Add resources** (optional): Add lexicons, stopwords, or other linguistic resources

4. **Test it**:
   ```bash
   langquality pack validate path/to/your_pack
   langquality analyze --input test_data --output results --language <your_language_code>
   ```

See the [Language Pack Guide](docs/language_pack_guide.md) for detailed instructions.

## 📖 Documentation

- **[Quickstart Guide](docs/quickstart.md)**: Get up and running in 5 minutes
- **[User Guide](docs/user_guide/)**: Comprehensive usage documentation
  - [Installation](docs/user_guide/installation.md)
  - [Analyzing Data](docs/user_guide/analyzing_data.md)
- **[Language Pack Guide](docs/language_pack_guide.md)**: Create and customize Language Packs
- **[Developer Guide](docs/developer_guide/)**: Extend LangQuality
  - [Architecture](docs/developer_guide/architecture.md)
  - [Creating Analyzers](docs/developer_guide/creating_analyzers.md)
  - [Plugin System](docs/developer_guide/plugin_system.md)
- **[API Reference](docs/api_reference/)**: Complete API documentation
- **[FAQ](docs/faq.md)**: Frequently asked questions
- **[Migration Guide](docs/migration_guide.md)**: Migrating from fongbe-data-quality

## 🎯 Use Cases

LangQuality is designed for researchers and developers working with low-resource languages:

- **ASR Dataset Preparation**: Ensure text quality before audio recording
- **Machine Translation**: Validate parallel corpora quality
- **Language Model Training**: Assess dataset diversity and balance
- **Corpus Linguistics**: Analyze linguistic properties of text collections
- **Data Curation**: Filter and improve existing datasets

## 🔧 Advanced Features

### Custom Configuration

Override default thresholds and settings:

```bash
langquality analyze --input data --output results --language fon --config my_config.yaml
```

Example configuration:

```yaml
thresholds:
  structural:
    min_words: 5
    max_words: 15
  diversity:
    target_ttr: 0.65
  gender:
    target_ratio: [0.45, 0.55]
```

### Custom Analyzers

Create custom analyzers for specialized analysis:

```python
from langquality.analyzers import Analyzer

class ToneAnalyzer(Analyzer):
    """Analyze tone and sentiment of sentences."""
    
    def analyze(self, sentences):
        # Your analysis logic
        return metrics
    
    def get_requirements(self):
        return ["tone_lexicon"]  # Required resources
```

Place your analyzer in the plugins directory and it will be automatically discovered.

See [Creating Analyzers](docs/developer_guide/creating_analyzers.md) for details.

## 🤝 Contributing

We welcome contributions from the community! Whether you're:
- 🌍 Creating a Language Pack for your language
- 🔧 Adding new analyzers or features
- 📝 Improving documentation
- 🐛 Reporting bugs or issues
- 💡 Suggesting enhancements

Please see our [Contributing Guide](CONTRIBUTING.md) for:
- Code of Conduct
- Development setup
- Contribution workflow
- Coding standards
- Testing requirements

### Quick Contribution Steps

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Ensure tests pass: `pytest`
5. Commit: `git commit -m 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 👥 Community

Join our community to get help, share ideas, and collaborate:

- **[GitHub Discussions](https://github.com/laleye/langquality/discussions)**: Ask questions, share ideas, showcase your Language Packs
- **[Issue Tracker](https://github.com/laleye/langquality/issues)**: Report bugs, request features
- **[Documentation](https://langquality.readthedocs.io/)**: Comprehensive guides and API reference
- **[Contributing Guide](CONTRIBUTING.md)**: Learn how to contribute
- **[Code of Conduct](CODE_OF_CONDUCT.md)**: Our community standards

### Support Channels

- 💬 **Questions**: Use [GitHub Discussions Q&A](https://github.com/laleye/langquality/discussions/categories/q-a)
- 🐛 **Bug Reports**: Open an [issue](https://github.com/laleye/langquality/issues/new?template=bug_report.md)
- 💡 **Feature Requests**: Open an [issue](https://github.com/laleye/langquality/issues/new?template=feature_request.md)
- 🌍 **Language Pack Submissions**: Use our [Language Pack template](https://github.com/laleye/langquality/issues/new?template=language_pack_submission.md)

## 📊 Project Status

LangQuality is actively maintained and under continuous development. See our [CHANGELOG](CHANGELOG.md) for recent updates and our [Roadmap](docs/roadmap.md) for planned features.

Current version: **1.0.0** (Stable)

## 📜 License

LangQuality is released under the [MIT License](LICENSE). You are free to use, modify, and distribute this software for any purpose, including commercial applications.

## 🙏 Acknowledgments

LangQuality evolved from the Fongbe Data Quality Pipeline, originally developed to support dataset creation for Fongbe, a low-resource language from Benin. We're grateful to:

- The linguistic community working on African language preservation and NLP development
- Contributors who have created Language Packs and shared their expertise
- The open-source NLP community for tools and libraries that make this work possible

## 📚 Citation

If you use LangQuality in your research, please cite:

```bibtex
@software{langquality_toolkit,
  title={LangQuality: Language Quality Toolkit for Low-Resource Languages},
  author={LangQuality Community},
  year={2024},
  url={https://github.com/langquality/langquality},
  version={1.0.0}
}
```

## 🔗 Related Projects

- **[Common Voice](https://commonvoice.mozilla.org/)**: Crowdsourced voice dataset
- **[FLORES](https://github.com/facebookresearch/flores)**: Multilingual translation benchmark
- **[Masakhane](https://www.masakhane.io/)**: African NLP community

---

**Made with ❤️ for low-resource language communities worldwide**

[Get Started](docs/quickstart.md) | [Documentation](https://langquality.readthedocs.io/) | [Community](https://github.com/laleye/langquality/discussions) | [Contributing](CONTRIBUTING.md)
