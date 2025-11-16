# Plugin System Guide

This guide explains LangQuality's plugin system, which allows you to extend functionality without modifying core code.

## Overview

The plugin system enables:
- **Dynamic Analyzer Loading** - Discover and load analyzers at runtime
- **Language Pack Extensions** - Add custom analyzers to language packs
- **Third-Party Plugins** - Distribute analyzers as separate packages
- **Hot Reloading** - Load plugins without restarting (future feature)

## Plugin Architecture

### Components

```
┌─────────────────────────────────────────────────────────┐
│                  Analyzer Registry                       │
│  - Discovers plugins                                     │
│  - Validates interfaces                                  │
│  - Manages analyzer lifecycle                            │
└────────────────┬────────────────────────────────────────┘
                 │
    ┌────────────┴────────────┐
    │                         │
┌───▼──────────┐    ┌────────▼─────────┐
│  Built-in    │    │   Plugin         │
│  Analyzers   │    │   Analyzers      │
│              │    │                  │
│ - Structural │    │ - Custom         │
│ - Linguistic │    │ - Third-party    │
│ - Diversity  │    │ - Language-      │
│ - Domain     │    │   specific       │
│ - Gender     │    │                  │
└──────────────┘    └──────────────────┘
```

### Plugin Discovery Process

1. **Scan Plugin Directories**
   - Language pack `analyzers/` directories
   - System plugin directory
   - User-specified directories

2. **Import Modules**
   - Dynamic import using `importlib`
   - Handle import errors gracefully

3. **Find Analyzer Classes**
   - Inspect module for `Analyzer` subclasses
   - Exclude abstract base classes

4. **Validate Interface**
   - Check required methods exist
   - Verify method signatures

5. **Register Analyzers**
   - Add to registry with unique names
   - Handle name conflicts

## Creating Plugins

### Basic Plugin Structure

```python
# my_plugin.py
from langquality.analyzers.base import Analyzer
from langquality.data.models import Sentence, AnalysisMetrics
from typing import List

class MyCustomAnalyzer(Analyzer):
    """Custom analyzer description."""
    
    def get_requirements(self) -> List[str]:
        """Return required resources."""
        return []
    
    def analyze(self, sentences: List[Sentence]) -> AnalysisMetrics:
        """Perform analysis."""
        # Implementation
        return AnalysisMetrics(
            name="my_custom",
            metrics={"example_metric": 42}
        )
```

### Plugin with Resources

```python
# sentiment_plugin.py
from langquality.analyzers.base import Analyzer
from langquality.data.models import Sentence, AnalysisMetrics
from typing import List, Dict
import json

class SentimentPlugin(Analyzer):
    """Sentiment analysis plugin."""
    
    def __init__(self, config, language_pack=None):
        super().__init__(config, language_pack)
        self.lexicon = self._load_lexicon()
    
    def get_requirements(self) -> List[str]:
        """Requires sentiment lexicon."""
        return ["sentiment_lexicon"]
    
    def _load_lexicon(self) -> Dict[str, float]:
        """Load sentiment lexicon from language pack."""
        if not self.language_pack:
            return {}
        
        lexicon_data = self.language_pack.get_resource("sentiment_lexicon")
        if lexicon_data:
            return json.loads(lexicon_data)
        return {}
    
    def analyze(self, sentences: List[Sentence]) -> AnalysisMetrics:
        """Analyze sentiment."""
        scores = [self._score_sentence(s) for s in sentences]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        return AnalysisMetrics(
            name="sentiment",
            metrics={
                "avg_sentiment": avg_score,
                "positive_count": sum(1 for s in scores if s > 0),
                "negative_count": sum(1 for s in scores if s < 0)
            }
        )
    
    def _score_sentence(self, sentence: Sentence) -> float:
        """Score a single sentence."""
        if not sentence.tokens:
            return 0.0
        
        scores = [
            self.lexicon.get(token.lower(), 0.0)
            for token in sentence.tokens
        ]
        return sum(scores) / len(scores) if scores else 0.0
```

### Plugin with Dependencies

```python
# ml_plugin.py
from langquality.analyzers.base import Analyzer
from langquality.data.models import Sentence, AnalysisMetrics
from typing import List, Tuple, Optional

try:
    import torch
    from transformers import pipeline
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

class MLSentimentAnalyzer(Analyzer):
    """ML-based sentiment analysis using transformers."""
    
    def __init__(self, config, language_pack=None):
        super().__init__(config, language_pack)
        self.model = self._load_model() if HAS_TRANSFORMERS else None
    
    def get_requirements(self) -> List[str]:
        """No language pack resources needed."""
        return []
    
    def can_run(self) -> Tuple[bool, Optional[str]]:
        """Check if transformers is available."""
        if not HAS_TRANSFORMERS:
            return False, "transformers library not installed"
        if not self.model:
            return False, "Failed to load model"
        return True, None
    
    def _load_model(self):
        """Load pre-trained sentiment model."""
        try:
            return pipeline("sentiment-analysis")
        except Exception as e:
            self.logger.error(f"Failed to load model: {e}")
            return None
    
    def analyze(self, sentences: List[Sentence]) -> AnalysisMetrics:
        """Analyze sentiment using ML model."""
        results = self.model([s.text for s in sentences])
        
        positive = sum(1 for r in results if r['label'] == 'POSITIVE')
        negative = sum(1 for r in results if r['label'] == 'NEGATIVE')
        
        return AnalysisMetrics(
            name="ml_sentiment",
            metrics={
                "positive_count": positive,
                "negative_count": negative,
                "positive_ratio": positive / len(sentences),
                "avg_confidence": sum(r['score'] for r in results) / len(results)
            }
        )
```

## Loading Plugins

### Method 1: Language Pack Plugins

Add plugins to language pack configuration:

```yaml
# language_packs/eng/config.yaml
plugins:
  - "analyzers/sentiment_plugin.py"
  - "analyzers/readability_plugin.py"
```

Directory structure:
```
language_packs/eng/
├── analyzers/
│   ├── sentiment_plugin.py
│   └── readability_plugin.py
├── resources/
│   └── sentiment_lexicon.json
└── config.yaml
```

Plugins are automatically loaded when the language pack is loaded:

```python
from langquality.language_packs.manager import LanguagePackManager

pack_manager = LanguagePackManager()
pack = pack_manager.load_language_pack('eng')
# Plugins are now loaded and registered
```

### Method 2: System Plugin Directory

Place plugins in a system directory:

```
~/.langquality/plugins/
├── sentiment_plugin.py
├── readability_plugin.py
└── custom_analyzer.py
```

Configure in `~/.langquality/config.yaml`:
```yaml
plugin_directories:
  - "~/.langquality/plugins"
  - "/usr/local/share/langquality/plugins"
```

### Method 3: Programmatic Loading

Load plugins programmatically:

```python
from langquality.analyzers.registry import AnalyzerRegistry

registry = AnalyzerRegistry()

# Discover plugins in directory
registry.discover_plugins("path/to/plugins/")

# Register specific analyzer
from my_plugin import MyCustomAnalyzer
registry.register("my_custom", MyCustomAnalyzer)
```

### Method 4: Entry Points (PyPI Packages)

Distribute plugins as PyPI packages with entry points:

```python
# setup.py
from setuptools import setup

setup(
    name="langquality-sentiment-plugin",
    version="1.0.0",
    py_modules=["sentiment_plugin"],
    install_requires=["langquality>=1.0.0"],
    entry_points={
        "langquality.analyzers": [
            "sentiment = sentiment_plugin:SentimentPlugin"
        ]
    }
)
```

Install and use:
```bash
pip install langquality-sentiment-plugin
```

The plugin is automatically discovered via entry points.

## Plugin Validation

### Interface Validation

The registry validates that plugins implement the required interface:

```python
class AnalyzerRegistry:
    def validate_analyzer(self, analyzer_class: Type[Analyzer]) -> bool:
        """Validate analyzer interface."""
        # Check inheritance
        if not issubclass(analyzer_class, Analyzer):
            return False
        
        # Check required methods
        required_methods = ['analyze', 'get_requirements']
        for method in required_methods:
            if not hasattr(analyzer_class, method):
                return False
        
        # Check method signatures
        analyze_sig = inspect.signature(analyzer_class.analyze)
        if len(analyze_sig.parameters) != 2:  # self, sentences
            return False
        
        return True
```

### Resource Validation

Plugins can validate their resources:

```python
class MyPlugin(Analyzer):
    def can_run(self) -> Tuple[bool, Optional[str]]:
        """Validate resources before running."""
        # Check required resources
        for resource in self.get_requirements():
            if not self.language_pack.has_resource(resource):
                return False, f"Missing resource: {resource}"
        
        # Check resource format
        lexicon = self.language_pack.get_resource("lexicon")
        if not isinstance(lexicon, dict):
            return False, "Invalid lexicon format"
        
        return True, None
```

## Plugin Configuration

### Plugin-Specific Configuration

Plugins can access configuration:

```python
class ConfigurablePlugin(Analyzer):
    def __init__(self, config, language_pack=None):
        super().__init__(config, language_pack)
        
        # Get plugin-specific config
        plugin_config = config.get('my_plugin', {})
        self.threshold = plugin_config.get('threshold', 0.5)
        self.mode = plugin_config.get('mode', 'default')
```

Configure in language pack:

```yaml
# config.yaml
thresholds:
  my_plugin:
    threshold: 0.7
    mode: "advanced"
```

### Runtime Configuration

Pass configuration at runtime:

```python
from langquality.pipeline.controller import PipelineController

# Custom configuration
config = {
    'my_plugin': {
        'threshold': 0.8,
        'mode': 'strict'
    }
}

controller = PipelineController(language_pack, config=config)
results = controller.run(sentences)
```

## Plugin Dependencies

### Handling Optional Dependencies

```python
# Check for optional dependencies
try:
    import optional_library
    HAS_OPTIONAL = True
except ImportError:
    HAS_OPTIONAL = False

class OptionalPlugin(Analyzer):
    def can_run(self) -> Tuple[bool, Optional[str]]:
        if not HAS_OPTIONAL:
            return False, "optional_library not installed"
        return True, None
```

### Declaring Dependencies

Document dependencies in plugin docstring:

```python
class MLPlugin(Analyzer):
    """
    ML-based analyzer using transformers.
    
    Dependencies:
        - torch>=1.9.0
        - transformers>=4.0.0
    
    Installation:
        pip install torch transformers
    """
```

Or in `setup.py` for distributed plugins:

```python
setup(
    name="langquality-ml-plugin",
    install_requires=[
        "langquality>=1.0.0",
        "torch>=1.9.0",
        "transformers>=4.0.0"
    ],
    extras_require={
        "gpu": ["torch-cuda>=1.9.0"]
    }
)
```

## Plugin Lifecycle

### Initialization

```python
class MyPlugin(Analyzer):
    def __init__(self, config, language_pack=None):
        super().__init__(config, language_pack)
        # Initialize resources
        self.model = self._load_model()
        self.cache = {}
```

### Execution

```python
def analyze(self, sentences: List[Sentence]) -> AnalysisMetrics:
    # Pre-processing
    self._prepare_data(sentences)
    
    # Analysis
    results = self._compute_metrics(sentences)
    
    # Post-processing
    self._cleanup()
    
    return AnalysisMetrics(name=self.name, metrics=results)
```

### Cleanup

```python
def __del__(self):
    """Cleanup resources."""
    if hasattr(self, 'model'):
        del self.model
    if hasattr(self, 'cache'):
        self.cache.clear()
```

## Error Handling

### Graceful Degradation

```python
class RobustPlugin(Analyzer):
    def analyze(self, sentences: List[Sentence]) -> AnalysisMetrics:
        try:
            return self._analyze_impl(sentences)
        except Exception as e:
            self.logger.error(f"Analysis failed: {e}")
            # Return empty metrics instead of crashing
            return AnalysisMetrics(
                name=self.name,
                metrics={"error": str(e)}
            )
```

### Error Reporting

```python
class VerbosePlugin(Analyzer):
    def analyze(self, sentences: List[Sentence]) -> AnalysisMetrics:
        errors = []
        results = []
        
        for i, sentence in enumerate(sentences):
            try:
                result = self._analyze_sentence(sentence)
                results.append(result)
            except Exception as e:
                errors.append({
                    "sentence_index": i,
                    "error": str(e)
                })
                self.logger.warning(f"Failed to analyze sentence {i}: {e}")
        
        return AnalysisMetrics(
            name=self.name,
            metrics={
                "results": results,
                "errors": errors,
                "success_rate": len(results) / len(sentences)
            }
        )
```

## Testing Plugins

### Unit Tests

```python
# test_my_plugin.py
import pytest
from my_plugin import MyCustomAnalyzer
from langquality.data.models import Sentence

def test_plugin_initialization():
    analyzer = MyCustomAnalyzer(config={})
    assert analyzer is not None

def test_plugin_requirements():
    analyzer = MyCustomAnalyzer(config={})
    requirements = analyzer.get_requirements()
    assert isinstance(requirements, list)

def test_plugin_analysis():
    analyzer = MyCustomAnalyzer(config={})
    
    sentences = [
        Sentence(
            text="Test sentence",
            domain="test",
            source_file="test.csv",
            line_number=1,
            char_count=13,
            word_count=2,
            tokens=["Test", "sentence"]
        )
    ]
    
    results = analyzer.analyze(sentences)
    
    assert results.name == "my_custom"
    assert "example_metric" in results.metrics
```

### Integration Tests

```python
# test_plugin_integration.py
import pytest
from langquality.pipeline.controller import PipelineController
from langquality.language_packs.manager import LanguagePackManager

def test_plugin_in_pipeline():
    # Load language pack with plugin
    pack_manager = LanguagePackManager()
    pack = pack_manager.load_language_pack('eng')
    
    # Run pipeline
    controller = PipelineController(pack)
    results = controller.run(test_sentences)
    
    # Check plugin results
    assert hasattr(results, 'my_custom')
    assert results.my_custom.metrics is not None
```

## Best Practices

### 1. Naming Conventions

```python
# Good: Descriptive, follows convention
class SentimentAnalyzer(Analyzer):
    pass

# Bad: Generic, unclear
class Plugin1(Analyzer):
    pass
```

### 2. Documentation

```python
class WellDocumentedPlugin(Analyzer):
    """
    Analyzes text sentiment using lexicon-based approach.
    
    This analyzer computes sentiment scores by matching words
    against a sentiment lexicon and aggregating scores.
    
    Requirements:
        - sentiment_lexicon: JSON file with word-score mappings
    
    Configuration:
        - threshold: Minimum confidence threshold (default: 0.5)
        - normalize: Whether to normalize scores (default: True)
    
    Example:
        >>> analyzer = WellDocumentedPlugin(config={})
        >>> results = analyzer.analyze(sentences)
        >>> print(results.metrics['avg_sentiment'])
    """
```

### 3. Resource Management

```python
class EfficientPlugin(Analyzer):
    def __init__(self, config, language_pack=None):
        super().__init__(config, language_pack)
        # Load resources once
        self._lexicon = None
    
    @property
    def lexicon(self):
        """Lazy load lexicon."""
        if self._lexicon is None:
            self._lexicon = self._load_lexicon()
        return self._lexicon
```

### 4. Performance

```python
class FastPlugin(Analyzer):
    def analyze(self, sentences: List[Sentence]) -> AnalysisMetrics:
        # Use vectorized operations
        import numpy as np
        
        scores = np.array([self._score(s) for s in sentences])
        
        return AnalysisMetrics(
            name=self.name,
            metrics={
                "avg": float(np.mean(scores)),
                "std": float(np.std(scores)),
                "min": float(np.min(scores)),
                "max": float(np.max(scores))
            }
        )
```

### 5. Versioning

```python
class VersionedPlugin(Analyzer):
    @property
    def version(self) -> str:
        return "1.2.0"
    
    def analyze(self, sentences: List[Sentence]) -> AnalysisMetrics:
        # Include version in results
        metrics = self._compute_metrics(sentences)
        metrics['analyzer_version'] = self.version
        
        return AnalysisMetrics(name=self.name, metrics=metrics)
```

## Distributing Plugins

### As PyPI Package

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="langquality-sentiment-plugin",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Sentiment analysis plugin for LangQuality",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/langquality-sentiment-plugin",
    packages=find_packages(),
    install_requires=[
        "langquality>=1.0.0",
    ],
    extras_require={
        "ml": ["transformers>=4.0.0", "torch>=1.9.0"]
    },
    entry_points={
        "langquality.analyzers": [
            "sentiment = sentiment_plugin:SentimentPlugin"
        ]
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
)
```

### As GitHub Repository

```bash
# Install from GitHub
pip install git+https://github.com/yourusername/langquality-sentiment-plugin.git

# Or clone and install
git clone https://github.com/yourusername/langquality-sentiment-plugin.git
cd langquality-sentiment-plugin
pip install -e .
```

## Troubleshooting

### Plugin Not Discovered

```python
# Check plugin directories
from langquality.analyzers.registry import AnalyzerRegistry

registry = AnalyzerRegistry()
print("Registered analyzers:", registry.list_analyzers())

# Manually discover
registry.discover_plugins("path/to/plugins/")
print("After discovery:", registry.list_analyzers())
```

### Import Errors

```python
# Check Python path
import sys
print("Python path:", sys.path)

# Add plugin directory to path
sys.path.insert(0, "path/to/plugins/")
```

### Interface Validation Fails

```python
# Validate manually
from langquality.analyzers.registry import AnalyzerRegistry
from my_plugin import MyPlugin

registry = AnalyzerRegistry()
is_valid = registry.validate_analyzer(MyPlugin)
print(f"Plugin valid: {is_valid}")
```

## Next Steps

- [Creating Analyzers Guide](creating_analyzers.md) - Learn to create analyzers
- [Architecture Guide](architecture.md) - Understand the system design
- [API Reference](../api_reference/) - Detailed API documentation
