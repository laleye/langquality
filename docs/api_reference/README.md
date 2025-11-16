# API Reference

Complete API documentation for LangQuality.

## Core Modules

### [analyzers](analyzers.md)
Analysis modules for evaluating text quality.

- `Analyzer` - Base analyzer class
- `StructuralAnalyzer` - Sentence structure analysis
- `LinguisticAnalyzer` - Readability and complexity
- `DiversityAnalyzer` - Vocabulary richness
- `DomainAnalyzer` - Thematic distribution
- `GenderBiasAnalyzer` - Gender representation
- `AnalyzerRegistry` - Plugin management

### [data](data.md)
Data loading and models.

- `GenericDataLoader` - Multi-format data loading
- `Sentence` - Sentence data model
- `Tokenizer` - Text tokenization interface
- `WhitespaceTokenizer` - Simple tokenization
- `SpacyTokenizer` - Linguistic tokenization
- `NLTKTokenizer` - NLTK-based tokenization

### [language_packs](language_packs.md)
Language pack system.

- `LanguagePackManager` - Pack discovery and loading
- `LanguagePack` - Language pack model
- `LanguageConfig` - Configuration model
- `PackMetadata` - Metadata model
- `PackValidator` - Validation utilities

### [pipeline](pipeline.md)
Pipeline orchestration.

- `PipelineController` - Main pipeline controller
- `AnalysisResults` - Results aggregation
- `AnalysisMetrics` - Metrics model

### [outputs](outputs.md)
Output generation and export.

- `DashboardGenerator` - HTML dashboard
- `ResultExporter` - Multi-format export
- `RecommendationEngine` - Recommendation generation

### [cli](cli.md)
Command-line interface.

- `analyze` - Run analysis
- `pack list` - List language packs
- `pack info` - Show pack details
- `pack create` - Create pack template
- `pack validate` - Validate pack

## Quick Reference

### Common Imports

```python
# Core functionality
from langquality.pipeline.controller import PipelineController
from langquality.language_packs.manager import LanguagePackManager
from langquality.data.generic_loader import GenericDataLoader

# Data models
from langquality.data.models import Sentence, AnalysisMetrics
from langquality.language_packs.models import LanguagePack

# Analyzers
from langquality.analyzers.base import Analyzer
from langquality.analyzers.registry import AnalyzerRegistry

# Output
from langquality.outputs.exporters import ResultExporter
```

### Basic Usage

```python
# Load language pack
pack_manager = LanguagePackManager()
pack = pack_manager.load_language_pack('eng')

# Load data
loader = GenericDataLoader(pack)
sentences = loader.load_from_csv('data.csv')

# Run analysis
controller = PipelineController(pack)
results = controller.run(sentences)

# Export results
exporter = ResultExporter('output/')
exporter.export_all(results)
```

## API Conventions

### Naming Conventions

- **Classes**: PascalCase (e.g., `LanguagePackManager`)
- **Functions/Methods**: snake_case (e.g., `load_language_pack`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_CONFIG`)
- **Private**: Leading underscore (e.g., `_internal_method`)

### Return Types

- **Success**: Return expected value or object
- **Not Found**: Return `None` or raise `NotFoundError`
- **Invalid Input**: Raise `ValueError` or `ValidationError`
- **System Error**: Raise appropriate exception with context

### Error Handling

```python
from langquality.utils.exceptions import (
    LangQualityError,
    LanguagePackError,
    AnalyzerError,
    ResourceNotFoundError,
    ConfigurationError
)
```

### Type Hints

All public APIs use type hints:

```python
def load_language_pack(self, code: str) -> LanguagePack:
    """Load a language pack by ISO 639-3 code."""
    pass

def analyze(self, sentences: List[Sentence]) -> AnalysisMetrics:
    """Perform analysis and return metrics."""
    pass
```

## Documentation Format

### Docstring Style

LangQuality uses Google-style docstrings:

```python
def example_function(param1: str, param2: int = 0) -> bool:
    """
    Brief description of function.
    
    Longer description with more details about what the function
    does and how it should be used.
    
    Args:
        param1: Description of param1
        param2: Description of param2 (default: 0)
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When param1 is empty
        TypeError: When param2 is not an integer
    
    Example:
        >>> result = example_function("test", 42)
        >>> print(result)
        True
    """
    pass
```

## Version Compatibility

### Semantic Versioning

LangQuality follows [Semantic Versioning](https://semver.org/):

- **Major** (1.x.x): Breaking changes
- **Minor** (x.1.x): New features, backward compatible
- **Patch** (x.x.1): Bug fixes, backward compatible

### Deprecation Policy

Deprecated features:
1. Marked with `@deprecated` decorator
2. Emit `DeprecationWarning`
3. Documented in CHANGELOG
4. Removed in next major version

Example:
```python
import warnings

@deprecated(version="1.1.0", alternative="new_function")
def old_function():
    warnings.warn(
        "old_function is deprecated, use new_function instead",
        DeprecationWarning,
        stacklevel=2
    )
    pass
```

## API Stability

### Stable APIs

Guaranteed backward compatibility within major versions:

- Core analyzers
- Data models
- Language pack structure
- CLI commands

### Experimental APIs

May change without notice:

- Plugin system internals
- Advanced configuration options
- Undocumented features

Marked with `@experimental` decorator:

```python
@experimental
def experimental_feature():
    """This API is experimental and may change."""
    pass
```

## Contributing to API

See [Contributing Guide](../../CONTRIBUTING.md) for:

- API design guidelines
- Documentation requirements
- Testing requirements
- Review process

## Support

- **Documentation**: [https://langquality.readthedocs.io](https://langquality.readthedocs.io)
- **Issues**: [GitHub Issues](https://github.com/langquality/langquality-toolkit/issues)
- **Discussions**: [GitHub Discussions](https://github.com/langquality/langquality-toolkit/discussions)
