# Creating Custom Analyzers

This guide explains how to create custom analyzers for LangQuality to extend its analysis capabilities.

## Overview

Analyzers are modular components that evaluate specific aspects of text quality. LangQuality includes built-in analyzers for structural, linguistic, diversity, domain, and gender bias analysis. You can create custom analyzers to add new analysis dimensions.

## Analyzer Interface

All analyzers must inherit from the `Analyzer` base class and implement its interface:

```python
from langquality.analyzers.base import Analyzer
from langquality.data.models import Sentence, AnalysisMetrics
from langquality.language_packs.models import LanguagePack
from typing import List, Tuple, Optional

class CustomAnalyzer(Analyzer):
    """Custom analyzer description."""
    
    def __init__(self, config, language_pack: Optional[LanguagePack] = None):
        super().__init__(config, language_pack)
        # Custom initialization
    
    def get_requirements(self) -> List[str]:
        """Return list of required resources."""
        return []
    
    def analyze(self, sentences: List[Sentence]) -> AnalysisMetrics:
        """Perform analysis and return metrics."""
        # Implementation
        pass
```

### Required Methods

#### `get_requirements() -> List[str]`

Returns a list of resource names required by the analyzer.

**Example**:
```python
def get_requirements(self) -> List[str]:
    return ["lexicon", "stopwords"]
```

If resources are missing, the analyzer will be skipped with a warning.

#### `analyze(sentences: List[Sentence]) -> AnalysisMetrics`

Performs the analysis and returns metrics.

**Parameters**:
- `sentences`: List of `Sentence` objects to analyze

**Returns**:
- `AnalysisMetrics`: Structured metrics from the analysis

**Example**:
```python
def analyze(self, sentences: List[Sentence]) -> AnalysisMetrics:
    # Compute metrics
    avg_length = sum(s.word_count for s in sentences) / len(sentences)
    
    return AnalysisMetrics(
        name="custom_analysis",
        metrics={
            "avg_length": avg_length,
            "total_sentences": len(sentences)
        }
    )
```

### Optional Methods

#### `can_run() -> Tuple[bool, Optional[str]]`

Checks if the analyzer can run with available resources. The base class provides a default implementation that checks `get_requirements()`.

Override for custom validation:

```python
def can_run(self) -> Tuple[bool, Optional[str]]:
    # Custom validation logic
    if not self.language_pack:
        return True, None  # No language-specific requirements
    
    if not self.language_pack.has_resource("custom_resource"):
        return False, "Missing custom_resource"
    
    return True, None
```

### Properties

#### `name` (property)

Returns the analyzer name. Default implementation returns the class name.

```python
@property
def name(self) -> str:
    return "CustomAnalyzer"
```

#### `version` (property)

Returns the analyzer version. Default is "1.0.0".

```python
@property
def version(self) -> str:
    return "1.0.0"
```

## Example: Sentiment Analyzer

Let's create a sentiment analyzer that evaluates the emotional tone of sentences.

### Step 1: Define the Analyzer Class

```python
# sentiment_analyzer.py
from langquality.analyzers.base import Analyzer
from langquality.data.models import Sentence, AnalysisMetrics
from langquality.language_packs.models import LanguagePack
from typing import List, Dict, Optional
import json

class SentimentAnalyzer(Analyzer):
    """Analyzes sentiment distribution in text data."""
    
    def __init__(self, config, language_pack: Optional[LanguagePack] = None):
        super().__init__(config, language_pack)
        self.sentiment_lexicon = self._load_sentiment_lexicon()
    
    def get_requirements(self) -> List[str]:
        """Requires sentiment lexicon resource."""
        return ["sentiment_lexicon"]
    
    def _load_sentiment_lexicon(self) -> Dict[str, float]:
        """Load sentiment lexicon from language pack."""
        if not self.language_pack:
            return {}
        
        lexicon_data = self.language_pack.get_resource("sentiment_lexicon")
        if not lexicon_data:
            return {}
        
        # Assume JSON format: {"word": sentiment_score}
        return json.loads(lexicon_data)
    
    def analyze(self, sentences: List[Sentence]) -> AnalysisMetrics:
        """Analyze sentiment distribution."""
        sentiment_scores = []
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for sentence in sentences:
            score = self._compute_sentiment_score(sentence)
            sentiment_scores.append(score)
            
            if score > 0.1:
                positive_count += 1
            elif score < -0.1:
                negative_count += 1
            else:
                neutral_count += 1
            
            # Store score in sentence metadata
            sentence.quality_scores['sentiment'] = score
        
        total = len(sentences)
        avg_sentiment = sum(sentiment_scores) / total if total > 0 else 0
        
        return AnalysisMetrics(
            name="sentiment",
            metrics={
                "avg_sentiment": avg_sentiment,
                "positive_ratio": positive_count / total if total > 0 else 0,
                "negative_ratio": negative_count / total if total > 0 else 0,
                "neutral_ratio": neutral_count / total if total > 0 else 0,
                "sentiment_distribution": {
                    "positive": positive_count,
                    "negative": negative_count,
                    "neutral": neutral_count
                }
            }
        )
    
    def _compute_sentiment_score(self, sentence: Sentence) -> float:
        """Compute sentiment score for a sentence."""
        if not sentence.tokens:
            return 0.0
        
        scores = []
        for token in sentence.tokens:
            token_lower = token.lower()
            if token_lower in self.sentiment_lexicon:
                scores.append(self.sentiment_lexicon[token_lower])
        
        return sum(scores) / len(scores) if scores else 0.0
    
    @property
    def name(self) -> str:
        return "SentimentAnalyzer"
    
    @property
    def version(self) -> str:
        return "1.0.0"
```

### Step 2: Create Sentiment Lexicon Resource

Create `resources/sentiment_lexicon.json` in your language pack:

```json
{
  "happy": 0.8,
  "sad": -0.7,
  "excellent": 0.9,
  "terrible": -0.9,
  "good": 0.6,
  "bad": -0.6,
  "love": 0.8,
  "hate": -0.8,
  "wonderful": 0.9,
  "awful": -0.8
}
```

### Step 3: Register the Analyzer

#### Option A: Add to Language Pack

Place the analyzer in your language pack's `analyzers/` directory:

```
language_packs/eng/
├── analyzers/
│   └── sentiment_analyzer.py
├── resources/
│   └── sentiment_lexicon.json
└── config.yaml
```

Update `config.yaml`:
```yaml
plugins:
  - "analyzers/sentiment_analyzer.py"

resources:
  sentiment_lexicon: "resources/sentiment_lexicon.json"
```

#### Option B: Register Programmatically

```python
from langquality.analyzers.registry import AnalyzerRegistry
from sentiment_analyzer import SentimentAnalyzer

registry = AnalyzerRegistry()
registry.register("sentiment", SentimentAnalyzer)
```

### Step 4: Use the Analyzer

```python
from langquality.pipeline.controller import PipelineController
from langquality.language_packs.manager import LanguagePackManager

# Load language pack
pack_manager = LanguagePackManager()
pack = pack_manager.load_language_pack('eng')

# Run analysis (includes custom analyzer)
controller = PipelineController(pack)
results = controller.run(sentences)

# Access sentiment metrics
print(results.sentiment.avg_sentiment)
print(results.sentiment.positive_ratio)
```

## Advanced Examples

### Example: Readability Analyzer

Analyzes text readability using multiple metrics:

```python
from langquality.analyzers.base import Analyzer
from langquality.data.models import Sentence, AnalysisMetrics
import textstat

class ReadabilityAnalyzer(Analyzer):
    """Analyzes text readability using multiple metrics."""
    
    def get_requirements(self) -> List[str]:
        return []  # No language-specific resources needed
    
    def analyze(self, sentences: List[Sentence]) -> AnalysisMetrics:
        """Compute readability metrics."""
        # Combine all text
        full_text = " ".join(s.text for s in sentences)
        
        # Compute various readability scores
        flesch_reading_ease = textstat.flesch_reading_ease(full_text)
        flesch_kincaid_grade = textstat.flesch_kincaid_grade(full_text)
        gunning_fog = textstat.gunning_fog(full_text)
        smog_index = textstat.smog_index(full_text)
        
        # Classify difficulty
        if flesch_reading_ease >= 60:
            difficulty = "easy"
        elif flesch_reading_ease >= 30:
            difficulty = "moderate"
        else:
            difficulty = "difficult"
        
        return AnalysisMetrics(
            name="readability",
            metrics={
                "flesch_reading_ease": flesch_reading_ease,
                "flesch_kincaid_grade": flesch_kincaid_grade,
                "gunning_fog": gunning_fog,
                "smog_index": smog_index,
                "difficulty": difficulty
            }
        )
```

### Example: Named Entity Analyzer

Analyzes named entity distribution:

```python
from langquality.analyzers.base import Analyzer
from langquality.data.models import Sentence, AnalysisMetrics
import spacy

class NamedEntityAnalyzer(Analyzer):
    """Analyzes named entity distribution."""
    
    def __init__(self, config, language_pack=None):
        super().__init__(config, language_pack)
        self.nlp = self._load_spacy_model()
    
    def get_requirements(self) -> List[str]:
        return []  # spaCy model loaded separately
    
    def _load_spacy_model(self):
        """Load spaCy model from language pack config."""
        if not self.language_pack:
            return None
        
        model_name = self.language_pack.config.tokenization.model
        if not model_name:
            return None
        
        try:
            return spacy.load(model_name)
        except OSError:
            self.logger.warning(f"spaCy model {model_name} not found")
            return None
    
    def can_run(self) -> Tuple[bool, Optional[str]]:
        """Check if spaCy model is available."""
        if not self.nlp:
            return False, "spaCy model not available"
        return True, None
    
    def analyze(self, sentences: List[Sentence]) -> AnalysisMetrics:
        """Analyze named entities."""
        entity_counts = {}
        total_entities = 0
        
        for sentence in sentences:
            doc = self.nlp(sentence.text)
            
            for ent in doc.ents:
                entity_counts[ent.label_] = entity_counts.get(ent.label_, 0) + 1
                total_entities += 1
        
        # Calculate entity diversity
        entity_types = len(entity_counts)
        entity_diversity = entity_types / total_entities if total_entities > 0 else 0
        
        return AnalysisMetrics(
            name="named_entities",
            metrics={
                "total_entities": total_entities,
                "entity_types": entity_types,
                "entity_diversity": entity_diversity,
                "entity_distribution": entity_counts,
                "avg_entities_per_sentence": total_entities / len(sentences)
            }
        )
```

### Example: Code-Switching Analyzer

Analyzes language mixing in multilingual text:

```python
from langquality.analyzers.base import Analyzer
from langquality.data.models import Sentence, AnalysisMetrics
from langdetect import detect, LangDetectException

class CodeSwitchingAnalyzer(Analyzer):
    """Analyzes code-switching patterns in multilingual text."""
    
    def __init__(self, config, language_pack=None):
        super().__init__(config, language_pack)
        self.primary_language = language_pack.code if language_pack else None
    
    def get_requirements(self) -> List[str]:
        return []
    
    def analyze(self, sentences: List[Sentence]) -> AnalysisMetrics:
        """Analyze code-switching patterns."""
        code_switched_count = 0
        language_distribution = {}
        
        for sentence in sentences:
            # Detect language for each sentence
            try:
                detected_lang = detect(sentence.text)
                language_distribution[detected_lang] = \
                    language_distribution.get(detected_lang, 0) + 1
                
                # Check if different from primary language
                if detected_lang != self.primary_language:
                    code_switched_count += 1
                    sentence.flags.append("code_switched")
            
            except LangDetectException:
                # Language detection failed
                pass
        
        total = len(sentences)
        code_switching_ratio = code_switched_count / total if total > 0 else 0
        
        return AnalysisMetrics(
            name="code_switching",
            metrics={
                "code_switched_count": code_switched_count,
                "code_switching_ratio": code_switching_ratio,
                "language_distribution": language_distribution,
                "primary_language": self.primary_language
            }
        )
```

## Best Practices

### 1. Resource Management

**Load resources efficiently**:
```python
def __init__(self, config, language_pack=None):
    super().__init__(config, language_pack)
    # Load resources once during initialization
    self.lexicon = self._load_lexicon()

def _load_lexicon(self):
    """Load lexicon with caching."""
    if not self.language_pack:
        return {}
    return self.language_pack.get_resource("lexicon", default={})
```

### 2. Error Handling

**Handle errors gracefully**:
```python
def analyze(self, sentences: List[Sentence]) -> AnalysisMetrics:
    try:
        # Analysis logic
        metrics = self._compute_metrics(sentences)
        return AnalysisMetrics(name=self.name, metrics=metrics)
    
    except Exception as e:
        self.logger.error(f"Analysis failed: {e}")
        # Return empty metrics or raise
        return AnalysisMetrics(name=self.name, metrics={})
```

### 3. Performance Optimization

**Use generators for large datasets**:
```python
def analyze(self, sentences: List[Sentence]) -> AnalysisMetrics:
    # Process in batches
    batch_size = 1000
    results = []
    
    for i in range(0, len(sentences), batch_size):
        batch = sentences[i:i + batch_size]
        batch_result = self._process_batch(batch)
        results.append(batch_result)
    
    # Aggregate results
    return self._aggregate_results(results)
```

### 4. Logging

**Use structured logging**:
```python
def analyze(self, sentences: List[Sentence]) -> AnalysisMetrics:
    self.logger.info(f"Starting {self.name} analysis")
    self.logger.debug(f"Processing {len(sentences)} sentences")
    
    # Analysis logic
    
    self.logger.info(f"Completed {self.name} analysis")
    return metrics
```

### 5. Configuration

**Support configurable thresholds**:
```python
def __init__(self, config, language_pack=None):
    super().__init__(config, language_pack)
    # Get analyzer-specific config
    self.threshold = config.get('sentiment_threshold', 0.5)
    self.min_confidence = config.get('min_confidence', 0.7)
```

### 6. Testing

**Write comprehensive tests**:
```python
# test_sentiment_analyzer.py
import pytest
from sentiment_analyzer import SentimentAnalyzer
from langquality.data.models import Sentence

def test_sentiment_analyzer():
    analyzer = SentimentAnalyzer(config={})
    
    sentences = [
        Sentence(text="I love this!", domain="test", 
                 source_file="test.csv", line_number=1,
                 char_count=13, word_count=3, tokens=["I", "love", "this"]),
        Sentence(text="This is terrible.", domain="test",
                 source_file="test.csv", line_number=2,
                 char_count=17, word_count=3, tokens=["This", "is", "terrible"])
    ]
    
    results = analyzer.analyze(sentences)
    
    assert results.name == "sentiment"
    assert "avg_sentiment" in results.metrics
    assert results.metrics["positive_ratio"] > 0
    assert results.metrics["negative_ratio"] > 0
```

## Registering Analyzers

### Method 1: Language Pack Plugin

Add to language pack's `config.yaml`:
```yaml
plugins:
  - "analyzers/sentiment_analyzer.py"
  - "analyzers/readability_analyzer.py"
```

### Method 2: Programmatic Registration

```python
from langquality.analyzers.registry import AnalyzerRegistry

registry = AnalyzerRegistry()
registry.register("sentiment", SentimentAnalyzer)
registry.register("readability", ReadabilityAnalyzer)
```

### Method 3: Auto-Discovery

Place analyzers in a plugin directory:
```
plugins/
├── sentiment_analyzer.py
├── readability_analyzer.py
└── named_entity_analyzer.py
```

Discover automatically:
```python
registry = AnalyzerRegistry()
registry.discover_plugins("plugins/")
```

## Distributing Analyzers

### As Part of Language Pack

Include analyzer in language pack distribution:
```
langquality-pack-english/
├── analyzers/
│   └── sentiment_analyzer.py
├── resources/
│   └── sentiment_lexicon.json
└── config.yaml
```

### As Standalone Package

Create a PyPI package:

```python
# setup.py
from setuptools import setup

setup(
    name="langquality-sentiment-analyzer",
    version="1.0.0",
    py_modules=["sentiment_analyzer"],
    install_requires=["langquality>=1.0.0"],
    entry_points={
        "langquality.analyzers": [
            "sentiment = sentiment_analyzer:SentimentAnalyzer"
        ]
    }
)
```

Install and use:
```bash
pip install langquality-sentiment-analyzer
```

## Troubleshooting

### Analyzer Not Found

```python
# Check if analyzer is registered
registry = AnalyzerRegistry()
print(registry.list_analyzers())
```

### Resource Loading Fails

```python
# Check if resource exists
pack = LanguagePackManager().load_language_pack('eng')
print(pack.has_resource("sentiment_lexicon"))
print(pack.get_resource("sentiment_lexicon"))
```

### Analyzer Skipped

Check logs for warnings:
```
WARNING - Skipping SentimentAnalyzer: Missing required resource: sentiment_lexicon
```

Ensure resources are configured in `config.yaml`.

## Next Steps

- [Plugin System Guide](plugin_system.md) - Learn about the plugin architecture
- [Architecture Guide](architecture.md) - Understand the system design
- [API Reference](../api_reference/) - Detailed API documentation
- [Contributing Guide](../../CONTRIBUTING.md) - Contribute your analyzer
