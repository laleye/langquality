# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.1] - 2025-11-25

### Fixed
- **Gender Bias Analyzer**: Fixed KeyError when accessing 'patterns' key in stereotype detection
  - Added validation to check stereotype data structure before accessing 'patterns'
  - Added graceful error handling with warning logs for malformed stereotype data
  - Improved `_load_stereotype_patterns` method with better validation
  - Analyzer now continues processing even when some stereotypes are invalid

## [1.0.0] - 2025-11-16

### Added

#### Core Architecture
- **Language Pack System**: Modular system for language-specific configurations and resources
  - Standardized directory structure for language packs
  - YAML-based configuration with validation
  - JSON metadata for pack information
  - Support for optional resources with graceful fallback
  - ISO 639-3 language code standard

- **Generic Data Loader**: Language-agnostic data loading
  - Support for CSV, JSON, JSONL, and TXT formats
  - Auto-detection of file format and text columns
  - Configurable tokenization based on language pack settings
  - Multiple tokenizer implementations (Spacy, NLTK, Whitespace)

- **Plugin System for Analyzers**: Extensible analyzer architecture
  - `AnalyzerRegistry` for dynamic analyzer discovery and loading
  - Base `Analyzer` class with language pack support
  - Resource requirement declaration and validation
  - Automatic plugin discovery from directories
  - Graceful degradation when resources are unavailable

- **Refactored Analyzers**: All analyzers updated for multi-language support
  - `StructuralAnalyzer`: Language-agnostic structural analysis
  - `LinguisticAnalyzer`: Configurable linguistic analysis
  - `DiversityAnalyzer`: Lexical diversity with optional resources
  - `DomainAnalyzer`: Domain balance analysis
  - `GenderBiasAnalyzer`: Configurable gender bias detection

#### Language Packs
- **Fongbe Language Pack** (`fon`): Complete migration from fongbe-quality
  - Lexicon with 5000+ entries
  - Gender terms and professions
  - ASR reference vocabulary
  - Comprehensive configuration

- **Template Language Pack**: Starter template for new languages
  - Documented configuration options
  - Example resource files
  - README with adaptation instructions

- **Minimal Language Pack** (`min`): Minimal viable configuration example

#### CLI Enhancements
- New `langquality` CLI with language pack support
  - `--language` flag for specifying language code
  - `langquality pack list`: List installed language packs
  - `langquality pack info <code>`: Display pack details
  - `langquality pack create <code>`: Generate new pack template
  - `langquality pack validate <path>`: Validate pack structure
- Backward compatibility alias: `fongbe-quality` → `langquality --language fon`
- Deprecation warnings for old CLI

#### Documentation
- Comprehensive user guide
- Language pack creation guide
- API reference documentation
- Migration guide from fongbe-quality
- Best practices documentation
- Configuration guide

#### Testing
- Unit tests for language pack system
- Unit tests for analyzer registry
- Unit tests for generic data loader
- Integration tests for multi-language pipeline
- Test fixtures for multiple languages
- >80% code coverage

#### Open Source Infrastructure
- GitHub issue templates (bug report, feature request, language pack submission)
- Pull request template with comprehensive checklist
- CODEOWNERS file for code review assignments
- CONTRIBUTING.md with detailed contribution guidelines
- CODE_OF_CONDUCT.md (Contributor Covenant 2.1)
- GOVERNANCE.md with project governance model
- MIT License

### Changed

#### Breaking Changes
- **Package renamed**: `fongbe-quality` → `langquality`
  - Module imports: `from fongbe_quality import ...` → `from langquality import ...`
  - CLI command: `fongbe-quality` → `langquality`
  - PyPI package: `fongbe-data-quality` → `langquality`

- **Configuration structure**: Language-specific settings moved to language packs
  - Old: Hardcoded in analyzer classes
  - New: Loaded from `language_packs/{code}/config.yaml`

- **Data loader interface**: Simplified and made language-agnostic
  - Old: `FongbeDataLoader` with hardcoded tokenization
  - New: `GenericDataLoader` with configurable tokenization

- **Analyzer initialization**: Now requires language pack parameter
  - Old: `analyzer = StructuralAnalyzer(config)`
  - New: `analyzer = StructuralAnalyzer(config, language_pack)`

- **Resource loading**: Resources now loaded from language packs
  - Old: Hardcoded paths in `src/fongbe_quality/resources/`
  - New: Dynamic loading from `language_packs/{code}/resources/`

#### Non-Breaking Changes
- Improved error messages with actionable suggestions
- Better logging throughout the pipeline
- Performance optimizations in data loading
- Enhanced validation for configurations

### Deprecated
- `fongbe_quality` module (use `langquality` instead)
- `fongbe-quality` CLI command (use `langquality --language fon`)
- Hardcoded resource paths (use language packs)

### Removed
- Fongbe-specific hardcoded configurations
- Language-specific code from core analyzers
- Deprecated utility functions

### Fixed
- UTF-8 BOM handling in CSV files
- Tokenization issues with non-Latin scripts
- Memory leaks in large dataset processing
- Race conditions in parallel processing

### Security
- Input validation for all configuration files
- Sandboxing for plugin execution
- Dependency vulnerability scanning in CI

## [0.1.0] - 2024 (fongbe-quality)

### Added
- Initial release as Fongbe Data Quality Pipeline
- Structural analysis for Fongbe text
- Linguistic analysis with French spaCy model
- Diversity analysis (TTR, unique words)
- Domain balance analysis
- Gender bias detection
- CSV data loading
- Dashboard generation
- PDF report generation
- CLI interface

---

## Migration Guide

### From fongbe-quality 0.1.0 to langquality 1.0.0

See [docs/migration_guide.md](docs/migration_guide.md) for detailed migration instructions.

#### Quick Migration Steps

1. **Update package installation**:
   ```bash
   pip uninstall fongbe-data-quality
   pip install langquality
   ```

2. **Update imports**:
   ```python
   # Old
   from fongbe_quality.pipeline import PipelineController
   
   # New
   from langquality.pipeline import PipelineController
   ```

3. **Update CLI commands**:
   ```bash
   # Old
   fongbe-quality analyze data.csv
   
   # New
   langquality analyze --language fon data.csv
   ```

4. **Migrate custom configurations**:
   - Move Fongbe-specific settings to `language_packs/fon/config.yaml`
   - Update resource file paths

5. **Update analyzer usage**:
   ```python
   # Old
   analyzer = StructuralAnalyzer(config)
   
   # New
   from langquality.language_packs import LanguagePackManager
   pack_manager = LanguagePackManager()
   pack = pack_manager.load_language_pack("fon")
   analyzer = StructuralAnalyzer(config, pack)
   ```

---

## Version History

- **1.0.0** (TBD): First stable release as LangQuality
- **0.1.0** (2024): Initial release as Fongbe Data Quality Pipeline

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for information on how to contribute to this project.

## Links

- [GitHub Repository](https://github.com/langquality/langquality-toolkit)
- [Documentation](https://langquality.readthedocs.io)
- [PyPI Package](https://pypi.org/project/langquality/)
- [Issue Tracker](https://github.com/langquality/langquality-toolkit/issues)
