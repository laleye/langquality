# LangQuality Documentation

Welcome to the LangQuality documentation! This directory contains comprehensive guides, tutorials, and reference materials for using and extending LangQuality.

## 📚 Documentation Structure

```
docs/
├── quickstart.md                    # Quick start guide (5 minutes)
├── user_guide/                      # User documentation
│   ├── installation.md              # Installation instructions
│   └── analyzing_data.md            # Data analysis guide
├── language_pack_guide.md           # Creating Language Packs
├── developer_guide/                 # Developer documentation
│   ├── architecture.md              # System architecture
│   ├── creating_analyzers.md        # Custom analyzer development
│   └── plugin_system.md             # Plugin system details
├── api_reference/                   # API documentation
│   └── README.md                    # API reference index
├── migration_guide.md               # Migration from fongbe-data-quality
├── data_loading_guide.md            # Data loading and formats
├── configuration_guide.md           # Configuration reference
├── best_practices.md                # Best practices for data quality
├── faq.md                          # Frequently asked questions
├── support.md                       # Getting help and support
├── roadmap.md                       # Project roadmap and future plans
├── maintainers.md                   # Project maintainers
├── development.md                   # Development setup
└── DOCUMENTATION_SUMMARY.md         # Documentation overview
```

## 🚀 Getting Started

### New Users
Start here if you're new to LangQuality:

1. **[Quickstart Guide](quickstart.md)** (5 min)
   - Install LangQuality
   - Run your first analysis
   - View results

2. **[Installation Guide](user_guide/installation.md)** (10 min)
   - Detailed installation instructions
   - System requirements
   - Troubleshooting

3. **[Analyzing Data](user_guide/analyzing_data.md)** (15 min)
   - Input data formats
   - Running analysis
   - Understanding results
   - Exporting data

### Language Pack Creators
Creating a Language Pack for your language:

1. **[Language Pack Guide](language_pack_guide.md)** (30 min)
   - Language Pack structure
   - Configuration options
   - Adding resources
   - Validation and testing

2. **[Data Loading Guide](data_loading_guide.md)** (15 min)
   - Supported formats
   - Tokenization options
   - Custom data loaders

### Developers
Extending LangQuality with custom functionality:

1. **[Architecture Overview](developer_guide/architecture.md)** (20 min)
   - System design
   - Core components
   - Data flow

2. **[Creating Analyzers](developer_guide/creating_analyzers.md)** (30 min)
   - Analyzer interface
   - Implementation guide
   - Best practices

3. **[Plugin System](developer_guide/plugin_system.md)** (20 min)
   - Plugin discovery
   - Registration
   - Testing plugins

4. **[Development Setup](development.md)** (15 min)
   - Setting up dev environment
   - Running tests
   - Contributing code

## 📖 Documentation by Topic

### Installation & Setup
- [Installation Guide](user_guide/installation.md) - Installing LangQuality
- [Configuration Guide](configuration_guide.md) - Configuring analysis parameters
- [Development Setup](development.md) - Setting up for development

### Using LangQuality
- [Quickstart](quickstart.md) - Get started in 5 minutes
- [Analyzing Data](user_guide/analyzing_data.md) - Complete analysis guide
- [Data Loading](data_loading_guide.md) - Loading different data formats
- [Best Practices](best_practices.md) - Data quality best practices

### Language Packs
- [Language Pack Guide](language_pack_guide.md) - Creating and using Language Packs
- [Configuration Reference](configuration_guide.md) - Configuration options
- [Migration Guide](migration_guide.md) - Migrating from fongbe-data-quality

### Extending LangQuality
- [Architecture](developer_guide/architecture.md) - System architecture
- [Creating Analyzers](developer_guide/creating_analyzers.md) - Custom analyzers
- [Plugin System](developer_guide/plugin_system.md) - Plugin development
- [API Reference](api_reference/) - Complete API documentation

### Reference
- [FAQ](faq.md) - Frequently asked questions
- [API Reference](api_reference/) - API documentation
- [Configuration Reference](configuration_guide.md) - All configuration options

### Community & Support
- [Support](support.md) - Getting help and support channels
- [Roadmap](roadmap.md) - Project roadmap and future plans
- [Maintainers](maintainers.md) - Project maintainers and governance

## 🎯 Documentation by Role

### Researchers
You want to analyze datasets for your low-resource language research:
- Start: [Quickstart](quickstart.md)
- Then: [Analyzing Data](user_guide/analyzing_data.md)
- Also: [Best Practices](best_practices.md)

### Linguists
You want to create a Language Pack for your language:
- Start: [Language Pack Guide](language_pack_guide.md)
- Then: [Configuration Guide](configuration_guide.md)
- Also: [Data Loading Guide](data_loading_guide.md)

### Developers
You want to extend LangQuality with custom analyzers:
- Start: [Architecture](developer_guide/architecture.md)
- Then: [Creating Analyzers](developer_guide/creating_analyzers.md)
- Also: [Plugin System](developer_guide/plugin_system.md)

### Contributors
You want to contribute to LangQuality:
- Start: [Development Setup](development.md)
- Then: [Architecture](developer_guide/architecture.md)
- Also: [CONTRIBUTING.md](../CONTRIBUTING.md)

## 🔍 Finding What You Need

### By Task

**I want to...**
- **Install LangQuality** → [Installation Guide](user_guide/installation.md)
- **Analyze my first dataset** → [Quickstart](quickstart.md)
- **Create a Language Pack** → [Language Pack Guide](language_pack_guide.md)
- **Understand the results** → [Analyzing Data](user_guide/analyzing_data.md)
- **Configure thresholds** → [Configuration Guide](configuration_guide.md)
- **Create a custom analyzer** → [Creating Analyzers](developer_guide/creating_analyzers.md)
- **Load different data formats** → [Data Loading Guide](data_loading_guide.md)
- **Migrate from fongbe-data-quality** → [Migration Guide](migration_guide.md)
- **Contribute code** → [Development Setup](development.md)
- **Find API details** → [API Reference](api_reference/)

### By Question

**Common questions:**
- "How do I install LangQuality?" → [Installation](user_guide/installation.md)
- "What languages are supported?" → [Language Pack Guide](language_pack_guide.md)
- "How do I create a Language Pack?" → [Language Pack Guide](language_pack_guide.md)
- "What data formats are supported?" → [Data Loading Guide](data_loading_guide.md)
- "How do I customize thresholds?" → [Configuration Guide](configuration_guide.md)
- "How do I create a custom analyzer?" → [Creating Analyzers](developer_guide/creating_analyzers.md)
- "How does the plugin system work?" → [Plugin System](developer_guide/plugin_system.md)
- "How do I contribute?" → [Development Setup](development.md) + [CONTRIBUTING.md](../CONTRIBUTING.md)
- "Where can I get help?" → [Support](support.md)
- "What's coming next?" → [Roadmap](roadmap.md)

More questions? Check the [FAQ](faq.md)!

## 📝 Documentation Standards

Our documentation follows these principles:

### Clarity
- Clear, concise language
- Step-by-step instructions
- Practical examples
- Visual aids where helpful

### Completeness
- Cover all features
- Include edge cases
- Provide troubleshooting
- Link to related topics

### Accessibility
- Multiple entry points
- Progressive disclosure
- Searchable content
- Multiple formats (web, PDF)

### Maintainability
- Version-controlled
- Regularly updated
- Community contributions welcome
- Automated builds

## 🌍 Translations

We welcome documentation translations! Currently available:
- **English** (primary)

Want to translate? See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## 🤝 Contributing to Documentation

Found an error? Want to improve the docs? We welcome contributions!

### Quick Fixes
For typos or small improvements:
1. Click "Edit this page" on any documentation page
2. Make your changes
3. Submit a Pull Request

### Major Changes
For new sections or significant rewrites:
1. Open an issue to discuss the changes
2. Fork the repository
3. Make your changes
4. Submit a Pull Request

See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed guidelines.

## 🔧 Building Documentation Locally

To build and preview the documentation locally:

### Using MkDocs (User Documentation)

```bash
# Install MkDocs
pip install mkdocs mkdocs-material

# Serve documentation locally
mkdocs serve

# Build static site
mkdocs build
```

### Using Sphinx (API Documentation)

```bash
# Install Sphinx
pip install sphinx sphinx-rtd-theme

# Build HTML documentation
cd docs
make html

# View in browser
open _build/html/index.html
```

## 📊 Documentation Status

| Section | Status | Last Updated |
|---------|--------|--------------|
| Quickstart | ✅ Complete | 2024-03 |
| User Guide | ✅ Complete | 2024-03 |
| Language Pack Guide | ✅ Complete | 2024-03 |
| Developer Guide | ✅ Complete | 2024-03 |
| API Reference | ✅ Complete | 2024-03 |
| Migration Guide | ✅ Complete | 2024-03 |
| FAQ | ✅ Complete | 2024-03 |
| Support | ✅ Complete | 2024-03 |
| Roadmap | ✅ Complete | 2024-03 |
| Maintainers | ✅ Complete | 2024-03 |

## 🔗 External Resources

### Related Documentation
- [Python Documentation](https://docs.python.org/) - Python language reference
- [spaCy Documentation](https://spacy.io/usage) - NLP library used by LangQuality
- [NLTK Documentation](https://www.nltk.org/) - Alternative NLP toolkit

### Community Resources
- [GitHub Discussions](https://github.com/langquality/langquality-toolkit/discussions) - Community Q&A
- [Issue Tracker](https://github.com/langquality/langquality-toolkit/issues) - Bug reports and features
- [Examples](../examples/) - Code examples and tutorials

### Academic Resources
- [Low-Resource NLP](https://github.com/neubig/lowresource-nlp-bootcamp2020) - Low-resource NLP resources
- [Masakhane](https://www.masakhane.io/) - African NLP community
- [Common Voice](https://commonvoice.mozilla.org/) - Multilingual speech dataset

## 📞 Getting Help

Can't find what you're looking for?

1. **Search the docs**: Use the search function (top of page)
2. **Check the FAQ**: [FAQ](faq.md) has common questions
3. **Read the support guide**: [Support](support.md) for all help channels
4. **Ask the community**: [GitHub Discussions](https://github.com/langquality/langquality-toolkit/discussions)
5. **Report an issue**: [Issue Tracker](https://github.com/langquality/langquality-toolkit/issues)

## 📄 License

Documentation is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).  
Code examples in documentation are licensed under [MIT License](../LICENSE).

---

**Ready to get started?** → [Quickstart Guide](quickstart.md)

[Back to Main README](../README.md) | [Examples](../examples/) | [Contributing](../CONTRIBUTING.md)
