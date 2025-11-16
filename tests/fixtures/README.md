# Test Fixtures

This directory contains test fixtures for the LangQuality test suite.

## Structure

### Language Packs

- **test_complete/**: A complete language pack with all resources and configurations
  - Includes lexicon, stopwords, gender terms, professions, and stereotypes
  - All analyzers enabled
  - Used for testing full functionality

- **test_minimal/**: A minimal language pack with only required fields
  - No resources
  - Only structural analyzer enabled
  - Used for testing graceful degradation

- **test_invalid/**: An invalid language pack for testing validation
  - Missing required fields
  - Invalid configuration values
  - Used for testing error handling

### Datasets

- **test_english.csv**: English test sentences with various characteristics
- **test_french.csv**: French test sentences
- **test_fongbe.csv**: Fongbe test sentences

Each dataset includes:
- Sentences of varying lengths (short, normal, long)
- Different domains
- Gender-related content for bias testing

### Plugins

- **test_custom_analyzer.py**: A simple custom analyzer with no resource requirements
  - Tests basic plugin loading and execution
  
- **test_resource_analyzer.py**: An analyzer that requires lexicon resource
  - Tests resource dependency checking
  - Tests graceful degradation when resources are missing

## Usage

These fixtures are used throughout the test suite:

```python
# Load a test language pack
from tests.fixtures import get_test_pack_path

pack_path = get_test_pack_path("test_complete")
manager = LanguagePackManager(pack_path.parent)
pack = manager.load_language_pack("test_complete")

# Load test datasets
from tests.fixtures import get_test_dataset_path

dataset_path = get_test_dataset_path("test_english.csv")
loader = GenericDataLoader(pack)
sentences = loader.load_from_csv(dataset_path)

# Load test plugins
from tests.fixtures import get_test_plugin_dir

plugin_dir = get_test_plugin_dir()
registry = AnalyzerRegistry()
registry.discover_plugins(plugin_dir)
```
