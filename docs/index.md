# LangQuality Documentation

Welcome to LangQuality, a language-agnostic toolkit for analyzing text data quality for low-resource languages.

## What is LangQuality?

LangQuality is an open-source toolkit that helps researchers, linguists, and NLP practitioners evaluate and improve the quality of text datasets. Originally designed for Fongbe (a low-resource language from Benin), it now supports any language through a flexible Language Pack system.

## Key Features

- **Language-Agnostic**: Works with any language through Language Packs
- **Comprehensive Analysis**: Evaluates structure, linguistics, diversity, domain balance, and bias
- **Extensible**: Plugin system for custom analyzers
- **Interactive Dashboard**: Beautiful visualizations of analysis results
- **Actionable Recommendations**: Specific suggestions for improvement
- **Multiple Export Formats**: JSON, CSV, PDF, HTML

## Quick Start

### Installation

```bash
pip install langquality
```

### Basic Usage

```bash
langquality analyze --input data.csv --output results --language eng
```

### View Results

```bash
open results/dashboard.html
```

## Analysis Dimensions

### 1. Structural Analysis
- Sentence length distribution
- Character count statistics
- Outlier detection

### 2. Linguistic Analysis
- Readability scores
- Lexical complexity
- Jargon detection

### 3. Diversity Analysis
- Vocabulary richness (TTR)
- N-gram frequency
- Duplicate detection

### 4. Domain Analysis
- Thematic distribution
- Balance metrics
- Under/over-representation

### 5. Gender Bias Analysis
- Gender mention ratios
- Stereotype detection
- Profession analysis

## Supported Languages

LangQuality includes language packs for:

- **Fongbe** (fon) - Stable
- **French** (fra) - Stable
- **English** (eng) - Stable
- **Minangkabau** (min) - Minimal
- **Chuukese** (chk) - Experimental

Create your own language pack for any language! See the [Language Pack Guide](language_pack_guide.md).

## Use Cases

- **ASR Dataset Preparation**: Prepare text for speech recording
- **Translation Quality**: Validate parallel corpus quality
- **Corpus Analysis**: Analyze linguistic corpus balance
- **Data Collection**: Ensure high-quality text collection
- **Model Training**: Prepare datasets for NLP model training

## Documentation Structure

### For Users
- [Quick Start](quickstart.md) - Get started in 5 minutes
- [User Guide](user_guide/) - Comprehensive usage documentation
- [Language Pack Guide](language_pack_guide.md) - Work with different languages
- [FAQ](faq.md) - Common questions and solutions

### For Developers
- [Architecture](developer_guide/architecture.md) - System design and components
- [Creating Analyzers](developer_guide/creating_analyzers.md) - Build custom analyzers
- [Plugin System](developer_guide/plugin_system.md) - Extend functionality
- [API Reference](api_reference/) - Complete API documentation

### Examples
- [Jupyter Notebooks](examples/notebooks/) - Interactive tutorials
- [Custom Analyzers](examples/custom_analyzers/) - Example implementations
- [Use Cases](examples/use_cases/) - Real-world applications

## Community

- **GitHub**: [langquality/langquality-toolkit](https://github.com/langquality/langquality-toolkit)
- **Issues**: [Report bugs or request features](https://github.com/langquality/langquality-toolkit/issues)
- **Discussions**: [Ask questions and share ideas](https://github.com/langquality/langquality-toolkit/discussions)
- **Contributing**: [Contribution guidelines](CONTRIBUTING.md)

## License

LangQuality is open-source software released under the MIT License.

## Citation

If you use LangQuality in your research, please cite:

```bibtex
@software{langquality,
  title={LangQuality: Language Quality Toolkit for Low-Resource Languages},
  author={LangQuality Contributors},
  year={2024},
  url={https://github.com/langquality/langquality-toolkit},
  version={1.0.0}
}
```

## Getting Help

- **Documentation**: You're reading it!
- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and community support
- **Email**: community@langquality.org

## Next Steps

Ready to get started? Check out the [Quick Start Guide](quickstart.md) or dive into the [User Guide](user_guide/).

---

*LangQuality is developed and maintained by the open-source community. Contributions are welcome!*
