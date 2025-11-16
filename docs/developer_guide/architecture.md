# LangQuality Architecture

This document provides a comprehensive overview of LangQuality's architecture, design principles, and component interactions.

## Design Principles

### 1. Language Agnosticism

LangQuality is designed to work with any language without code modifications. Language-specific logic is encapsulated in Language Packs, while the core system remains language-neutral.

### 2. Modularity

The system is composed of independent, loosely-coupled modules that can be used separately or together:

- **Data Loading** - Independent of analysis
- **Analyzers** - Independent of each other
- **Output Generation** - Independent of analysis logic
- **Language Packs** - Self-contained language configurations

### 3. Extensibility

New functionality can be added without modifying core code:

- **Plugin System** - Dynamic analyzer discovery and loading
- **Custom Resources** - Add language-specific data
- **Custom Tokenizers** - Implement language-specific tokenization
- **Custom Exporters** - Add new output formats

### 4. Fail-Safe Operation

The system degrades gracefully when resources are unavailable:

- Missing resources disable specific analyzers
- Analyzer failures don't crash the pipeline
- Partial results are returned when possible
- Clear warnings inform users of limitations

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI Layer                            │
│                    (User Interface)                          │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   Pipeline Controller                        │
│              (Orchestration & Workflow)                      │
└─────┬──────────────────┬──────────────────┬─────────────────┘
      │                  │                  │
┌─────▼─────┐   ┌───────▼────────┐   ┌────▼──────────────────┐
│  Config   │   │  Data Loader   │   │  Analyzer Registry    │
│  Manager  │   │   (Generic)    │   │  (Plugin System)      │
└─────┬─────┘   └───────┬────────┘   └────┬──────────────────┘
      │                  │                  │
┌─────▼──────────────────▼──────────────────▼─────────────────┐
│              Language Pack System                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Language A  │  │  Language B  │  │  Language C  │      │
│  │  - config    │  │  - config    │  │  - config    │      │
│  │  - resources │  │  - resources │  │  - resources │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└──────────────────────────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    Analyzer Modules                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Structural│  │Linguistic│  │ Diversity│  │  Custom  │   │
│  │          │  │          │  │          │  │ Plugins  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└──────────────────────────────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   Output Generators                          │
│     (Dashboard, Reports, Exports, Recommendations)           │
└──────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. CLI Layer (`cli.py`)

**Responsibility**: User interface and command routing

**Key Functions**:
- Parse command-line arguments
- Validate user input
- Route commands to appropriate handlers
- Display results and errors

**Commands**:
- `analyze` - Run quality analysis
- `pack list` - List language packs
- `pack info` - Show pack details
- `pack create` - Generate pack template
- `pack validate` - Validate pack structure

**Example**:
```python
@click.command()
@click.option('--input', '-i', required=True)
@click.option('--output', '-o', required=True)
@click.option('--language', '-l', required=True)
@click.option('--config', '-c', default=None)
def analyze(input, output, language, config):
    """Run quality analysis on text data."""
    # Load language pack
    pack_manager = LanguagePackManager()
    pack = pack_manager.load_language_pack(language)
    
    # Run pipeline
    controller = PipelineController(pack)
    results = controller.run_from_path(input)
    
    # Generate outputs
    exporter = ResultExporter(output)
    exporter.export_all(results)
```

### 2. Language Pack System

#### LanguagePackManager (`language_packs/manager.py`)

**Responsibility**: Discover, load, and validate language packs

**Key Methods**:
```python
class LanguagePackManager:
    def load_language_pack(self, code: str) -> LanguagePack:
        """Load a language pack by ISO 639-3 code."""
        
    def list_available_packs(self) -> List[PackInfo]:
        """List all installed language packs."""
        
    def validate_pack(self, path: str) -> ValidationResult:
        """Validate pack structure and content."""
        
    def create_pack_template(self, code: str, output_dir: str):
        """Generate a new pack template."""
```

**Pack Discovery**:
1. Search `langquality/language_packs/packs/` directory
2. Look for directories with ISO 639-3 codes
3. Validate required files (`config.yaml`, `metadata.json`)
4. Load and cache pack configurations

#### LanguagePack (`language_packs/models.py`)

**Responsibility**: Represent a complete language pack

**Data Model**:
```python
@dataclass
class LanguagePack:
    code: str                          # ISO 639-3 code
    name: str                          # Language name
    config: LanguageConfig             # Configuration
    metadata: PackMetadata             # Metadata
    resources: Dict[str, Any]          # Loaded resources
    custom_analyzers: List[Type[Analyzer]]  # Custom analyzers
    
    def get_resource(self, name: str, default=None) -> Any:
        """Get a resource with fallback."""
        
    def has_resource(self, name: str) -> bool:
        """Check if resource is available."""
```

**Resource Loading**:
- Lazy loading - resources loaded on first access
- Caching - resources cached after first load
- Fallback - default values if resource missing
- Validation - resources validated on load

### 3. Data Loading System

#### GenericDataLoader (`data/generic_loader.py`)

**Responsibility**: Load text data from various formats

**Supported Formats**:
- CSV (with auto-detection of text column)
- JSON / JSONL
- Plain text (one sentence per line)

**Key Methods**:
```python
class GenericDataLoader:
    def __init__(self, language_pack: LanguagePack):
        self.language_pack = language_pack
        self.tokenizer = self._initialize_tokenizer()
    
    def load_from_csv(self, filepath: str, 
                      text_column: Optional[str] = None) -> List[Sentence]:
        """Load sentences from CSV."""
        
    def load_from_json(self, filepath: str,
                       text_field: str = "text") -> List[Sentence]:
        """Load sentences from JSON."""
        
    def auto_detect_format(self, filepath: str) -> str:
        """Auto-detect file format."""
```

**Text Column Detection**:
1. Check for explicit column name
2. Look for common names: `text`, `sentence`, `phrase`, `content`
3. Look for columns containing "text" in name
4. Use first column as fallback

#### Tokenizers (`data/tokenizers.py`)

**Responsibility**: Language-specific text tokenization

**Tokenizer Types**:

```python
class Tokenizer(ABC):
    @abstractmethod
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into words."""

class WhitespaceTokenizer(Tokenizer):
    """Simple whitespace-based tokenization."""
    
class SpacyTokenizer(Tokenizer):
    """spaCy-based linguistic tokenization."""
    
class NLTKTokenizer(Tokenizer):
    """NLTK-based tokenization."""
    
class CustomTokenizer(Tokenizer):
    """User-defined custom tokenization."""
```

**Tokenizer Selection**:
Based on language pack configuration:
```yaml
tokenization:
  method: "spacy"  # or "nltk", "whitespace", "custom"
  model: "en_core_web_md"
```

### 4. Analyzer System

#### Base Analyzer (`analyzers/base.py`)

**Responsibility**: Define analyzer interface and common functionality

**Interface**:
```python
class Analyzer(ABC):
    def __init__(self, config: AnalysisConfig, 
                 language_pack: Optional[LanguagePack] = None):
        self.config = config
        self.language_pack = language_pack
    
    @abstractmethod
    def analyze(self, sentences: List[Sentence]) -> AnalysisMetrics:
        """Perform analysis and return metrics."""
    
    @abstractmethod
    def get_requirements(self) -> List[str]:
        """Return list of required resources."""
    
    def can_run(self) -> Tuple[bool, Optional[str]]:
        """Check if analyzer can run with available resources."""
    
    @property
    def name(self) -> str:
        """Return analyzer name."""
    
    @property
    def version(self) -> str:
        """Return analyzer version."""
```

**Lifecycle**:
1. **Initialization** - Load configuration and language pack
2. **Validation** - Check if required resources are available
3. **Analysis** - Process sentences and compute metrics
4. **Results** - Return structured metrics

#### Built-in Analyzers

**StructuralAnalyzer** (`analyzers/structural.py`)
- Sentence length distribution
- Character count statistics
- Outlier detection
- No language-specific resources required

**LinguisticAnalyzer** (`analyzers/linguistic.py`)
- Readability scores (Flesch-Kincaid)
- Lexical complexity
- POS tagging (if spaCy available)
- Requires: tokenizer, optionally spaCy model

**DiversityAnalyzer** (`analyzers/diversity.py`)
- Type-Token Ratio (TTR)
- Unique word count
- N-gram frequency
- Near-duplicate detection
- Requires: tokenizer, optionally stopwords

**DomainAnalyzer** (`analyzers/domain.py`)
- Domain distribution
- Balance metrics
- Under/over-representation
- No language-specific resources required

**GenderBiasAnalyzer** (`analyzers/gender_bias.py`)
- Gender mention ratio
- Stereotype detection
- Profession analysis
- Requires: gender_terms.json, professions.json

#### Analyzer Registry (`analyzers/registry.py`)

**Responsibility**: Discover, register, and manage analyzers

**Key Methods**:
```python
class AnalyzerRegistry:
    def __init__(self):
        self._analyzers: Dict[str, Type[Analyzer]] = {}
        self._load_builtin_analyzers()
    
    def register(self, name: str, analyzer_class: Type[Analyzer]):
        """Register an analyzer."""
    
    def discover_plugins(self, plugin_dir: str):
        """Discover and load analyzer plugins."""
    
    def get_analyzer(self, name: str) -> Type[Analyzer]:
        """Get an analyzer class by name."""
    
    def list_analyzers(self) -> List[str]:
        """List all registered analyzers."""
```

**Plugin Discovery**:
1. Scan plugin directory for Python files
2. Import modules dynamically
3. Find classes inheriting from `Analyzer`
4. Validate interface compliance
5. Register discovered analyzers

### 5. Pipeline Controller

#### PipelineController (`pipeline/controller.py`)

**Responsibility**: Orchestrate the analysis workflow

**Workflow**:
```python
class PipelineController:
    def __init__(self, language_pack: LanguagePack,
                 analyzer_registry: Optional[AnalyzerRegistry] = None):
        self.language_pack = language_pack
        self.registry = analyzer_registry or AnalyzerRegistry()
        self.analyzers = self._initialize_analyzers()
    
    def run(self, sentences: List[Sentence]) -> AnalysisResults:
        """Run complete analysis pipeline."""
        results = AnalysisResults()
        
        for name, analyzer in self.analyzers.items():
            try:
                metrics = analyzer.analyze(sentences)
                results.add_metrics(name, metrics)
            except Exception as e:
                self.logger.error(f"Analyzer {name} failed: {e}")
                # Continue with other analyzers
        
        return results
```

**Analyzer Initialization**:
1. Get enabled analyzers from language pack config
2. Instantiate each analyzer with config and language pack
3. Check if analyzer can run (resources available)
4. Skip analyzers that can't run, log warnings
5. Return dictionary of runnable analyzers

**Error Handling**:
- Analyzer failures don't stop pipeline
- Errors logged with context
- Partial results returned
- Recommendations generated for failures

### 6. Output System

#### Dashboard Generator (`outputs/dashboard.py`)

**Responsibility**: Generate interactive HTML dashboard

**Features**:
- Plotly visualizations
- Responsive design
- Interactive charts
- Summary statistics
- Recommendations list

**Template System**:
Uses Jinja2 templates for HTML generation:
```python
from jinja2 import Template

template = Template(dashboard_template)
html = template.render(
    results=results,
    charts=charts,
    recommendations=recommendations
)
```

#### Exporters (`outputs/exporters.py`)

**Responsibility**: Export results in various formats

**Export Formats**:

```python
class ResultExporter:
    def export_json(self, results: AnalysisResults, path: str):
        """Export as JSON."""
    
    def export_csv(self, sentences: List[Sentence], path: str):
        """Export annotated sentences as CSV."""
    
    def export_pdf(self, results: AnalysisResults, path: str):
        """Export summary report as PDF."""
    
    def export_all(self, results: AnalysisResults, output_dir: str):
        """Export all formats."""
```

### 7. Recommendation Engine

#### RecommendationEngine (`recommendations/engine.py`)

**Responsibility**: Generate actionable recommendations

**Process**:
1. Analyze metrics from all analyzers
2. Compare against thresholds
3. Identify issues and their severity
4. Generate specific, actionable recommendations
5. Prioritize by severity and impact

**Recommendation Model**:
```python
@dataclass
class Recommendation:
    severity: str  # 'critical', 'warning', 'info'
    category: str  # 'structural', 'linguistic', etc.
    title: str
    description: str
    action: str
    impact: str
    affected_count: int
```

## Data Flow

### Analysis Pipeline Flow

```
1. User Input (CLI)
   ↓
2. Load Language Pack
   ↓
3. Load Data (CSV/JSON/TXT)
   ↓
4. Tokenize Sentences
   ↓
5. Initialize Analyzers
   ↓
6. Run Each Analyzer
   ├─ Structural Analysis
   ├─ Linguistic Analysis
   ├─ Diversity Analysis
   ├─ Domain Analysis
   └─ Gender Bias Analysis
   ↓
7. Aggregate Results
   ↓
8. Generate Recommendations
   ↓
9. Export Outputs
   ├─ Dashboard (HTML)
   ├─ Metrics (JSON)
   ├─ Annotated Data (CSV)
   └─ Report (PDF)
   ↓
10. Display Summary (CLI)
```

### Data Models

#### Sentence Model

```python
@dataclass
class Sentence:
    text: str
    domain: str
    source_file: str
    line_number: int
    
    # Computed fields
    char_count: int
    word_count: int
    tokens: Optional[List[str]] = None
    
    # Language metadata
    language_code: Optional[str] = None
    script: Optional[str] = None
    
    # Analysis results
    quality_scores: Dict[str, float] = field(default_factory=dict)
    flags: List[str] = field(default_factory=list)
    
    # Extensible metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
```

#### Analysis Results Model

```python
@dataclass
class AnalysisResults:
    metadata: AnalysisMetadata
    structural: StructuralMetrics
    linguistic: LinguisticMetrics
    diversity: DiversityMetrics
    domain: DomainMetrics
    gender_bias: GenderBiasMetrics
    recommendations: List[Recommendation]
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON export."""
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert to pandas DataFrame."""
```

## Extension Points

### 1. Custom Analyzers

Create new analyzers by inheriting from `Analyzer`:

```python
from langquality.analyzers.base import Analyzer

class SentimentAnalyzer(Analyzer):
    def get_requirements(self) -> List[str]:
        return ["sentiment_lexicon"]
    
    def analyze(self, sentences: List[Sentence]) -> AnalysisMetrics:
        # Implementation
        pass
```

Place in language pack's `analyzers/` directory or register programmatically.

### 2. Custom Tokenizers

Implement language-specific tokenization:

```python
from langquality.data.tokenizers import Tokenizer

class ArabicTokenizer(Tokenizer):
    def tokenize(self, text: str) -> List[str]:
        # Handle Arabic-specific features
        # - Right-to-left text
        # - Diacritics
        # - Word boundaries
        pass
```

### 3. Custom Resources

Add language-specific data:

```yaml
resources:
  custom:
    - "resources/custom/domain_keywords.json"
    - "resources/custom/idioms.txt"
```

Access in analyzers:
```python
keywords = self.language_pack.get_resource("domain_keywords")
```

### 4. Custom Exporters

Add new output formats:

```python
class MarkdownExporter:
    def export(self, results: AnalysisResults, path: str):
        # Generate Markdown report
        pass
```

## Performance Considerations

### Optimization Strategies

1. **Lazy Loading**
   - Resources loaded only when needed
   - Analyzers initialized on demand

2. **Caching**
   - Language packs cached after first load
   - Tokenization results cached
   - Resource files cached in memory

3. **Parallel Processing** (Future)
   - Analyze multiple files in parallel
   - Run independent analyzers concurrently

4. **Streaming** (Future)
   - Process large files in chunks
   - Reduce memory footprint

### Memory Management

- Use generators for large datasets
- Clear caches when memory constrained
- Batch processing for very large files

### Profiling

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Run analysis
controller.run(sentences)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)
```

## Testing Architecture

### Test Structure

```
tests/
├── unit/                    # Unit tests
│   ├── test_analyzers.py
│   ├── test_data_loader.py
│   ├── test_language_pack_manager.py
│   └── test_tokenizers.py
├── integration/             # Integration tests
│   ├── test_pipeline.py
│   └── test_plugin_system.py
├── fixtures/                # Test data
│   ├── language_packs/
│   └── datasets/
└── e2e/                     # End-to-end tests
    └── test_full_workflow.py
```

### Testing Strategies

1. **Unit Tests** - Test individual components in isolation
2. **Integration Tests** - Test component interactions
3. **E2E Tests** - Test complete workflows
4. **Fixture-Based** - Use realistic test data
5. **Property-Based** - Use hypothesis for edge cases

## Security Considerations

### Input Validation

- Validate all file paths
- Sanitize user input
- Check file sizes before loading
- Validate configuration schemas

### Plugin Sandboxing

- Validate plugin interfaces
- Catch and log plugin errors
- Limit plugin resource access
- Review plugin code before loading

### Dependency Management

- Pin dependency versions
- Scan for vulnerabilities
- Regular security updates
- Minimal dependency footprint

## Future Architecture Enhancements

### Planned Features

1. **Async/Await Support**
   - Asynchronous analyzer execution
   - Non-blocking I/O operations

2. **Distributed Processing**
   - Process datasets across multiple machines
   - Cloud-based analysis

3. **Real-time Analysis**
   - Stream processing
   - Incremental updates

4. **ML-Based Analysis**
   - Learned quality metrics
   - Automatic threshold tuning
   - Anomaly detection

5. **Web API**
   - REST API for remote analysis
   - WebSocket for real-time updates
   - Web-based dashboard

## References

- [Design Document](../../.kiro/specs/generalize-low-resource-toolkit/design.md)
- [Requirements Document](../../.kiro/specs/generalize-low-resource-toolkit/requirements.md)
- [Plugin System Guide](plugin_system.md)
- [Creating Analyzers Guide](creating_analyzers.md)
