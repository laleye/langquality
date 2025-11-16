"""Unit tests for AnalyzerRegistry."""

import pytest
from pathlib import Path

from src.langquality.analyzers.registry import AnalyzerRegistry
from src.langquality.analyzers.base import Analyzer
from src.langquality.analyzers.structural import StructuralAnalyzer
from src.langquality.analyzers.linguistic import LinguisticAnalyzer
from src.langquality.analyzers.diversity import DiversityAnalyzer
from src.langquality.analyzers.domain import DomainAnalyzer
from src.langquality.analyzers.gender_bias import GenderBiasAnalyzer
from tests.fixtures import get_test_plugin_dir


class TestAnalyzerRegistry:
    """Tests for AnalyzerRegistry class."""
    
    def test_initialization(self):
        """Test registry initialization."""
        registry = AnalyzerRegistry()
        
        assert isinstance(registry._analyzers, dict)
        assert len(registry._analyzers) > 0
    
    def test_builtin_analyzers_loaded(self):
        """Test that built-in analyzers are loaded on init."""
        registry = AnalyzerRegistry()
        
        analyzers = registry.list_analyzers()
        assert "structural" in analyzers
        assert "linguistic" in analyzers
        assert "diversity" in analyzers
        assert "domain" in analyzers
        assert "gender_bias" in analyzers
    
    def test_get_analyzer(self):
        """Test getting an analyzer by name."""
        registry = AnalyzerRegistry()
        
        analyzer_class = registry.get_analyzer("structural")
        assert analyzer_class == StructuralAnalyzer
    
    def test_get_nonexistent_analyzer(self):
        """Test getting a non-existent analyzer raises error."""
        registry = AnalyzerRegistry()
        
        with pytest.raises(KeyError, match="not found"):
            registry.get_analyzer("nonexistent")
    
    def test_list_analyzers(self):
        """Test listing all analyzers."""
        registry = AnalyzerRegistry()
        
        analyzers = registry.list_analyzers()
        assert isinstance(analyzers, list)
        assert len(analyzers) >= 5  # At least 5 built-in analyzers
        assert all(isinstance(name, str) for name in analyzers)
    
    def test_has_analyzer(self):
        """Test checking if analyzer exists."""
        registry = AnalyzerRegistry()
        
        assert registry.has_analyzer("structural") is True
        assert registry.has_analyzer("nonexistent") is False
    
    def test_camel_to_snake_conversion(self):
        """Test CamelCase to snake_case conversion."""
        registry = AnalyzerRegistry()
        
        assert registry._camel_to_snake("StructuralAnalyzer") == "structural_analyzer"
        assert registry._camel_to_snake("GenderBias") == "gender_bias"
        assert registry._camel_to_snake("Simple") == "simple"


class TestAnalyzerRegistration:
    """Tests for analyzer registration."""
    
    def test_register_valid_analyzer(self):
        """Test registering a valid analyzer."""
        registry = AnalyzerRegistry()
        
        # Create a simple test analyzer
        class TestAnalyzer(Analyzer):
            def analyze(self, sentences):
                return {}
            
            def get_requirements(self):
                return []
            
            def can_run(self):
                return True, None
            
            @property
            def name(self):
                return "test"
            
            @property
            def version(self):
                return "1.0.0"
        
        initial_count = len(registry.list_analyzers())
        registry.register("test", TestAnalyzer)
        
        assert len(registry.list_analyzers()) == initial_count + 1
        assert registry.has_analyzer("test")
        assert registry.get_analyzer("test") == TestAnalyzer
    
    def test_register_non_class(self):
        """Test registering a non-class raises error."""
        registry = AnalyzerRegistry()
        
        with pytest.raises(TypeError, match="must be a class"):
            registry.register("invalid", "not a class")
    
    def test_register_non_analyzer_subclass(self):
        """Test registering non-Analyzer subclass raises error."""
        registry = AnalyzerRegistry()
        
        class NotAnAnalyzer:
            pass
        
        with pytest.raises(TypeError, match="must be a subclass"):
            registry.register("invalid", NotAnAnalyzer)
    
    def test_register_invalid_interface(self):
        """Test registering analyzer with invalid interface raises error."""
        registry = AnalyzerRegistry()
        
        # Missing required methods
        class IncompleteAnalyzer(Analyzer):
            pass
        
        with pytest.raises(ValueError, match="does not implement required interface"):
            registry.register("incomplete", IncompleteAnalyzer)
    
    def test_unregister_analyzer(self):
        """Test unregistering an analyzer."""
        registry = AnalyzerRegistry()
        
        assert registry.has_analyzer("structural")
        result = registry.unregister("structural")
        
        assert result is True
        assert not registry.has_analyzer("structural")
    
    def test_unregister_nonexistent(self):
        """Test unregistering non-existent analyzer."""
        registry = AnalyzerRegistry()
        
        result = registry.unregister("nonexistent")
        assert result is False
    
    def test_clear_registry(self):
        """Test clearing all analyzers."""
        registry = AnalyzerRegistry()
        
        assert len(registry.list_analyzers()) > 0
        registry.clear()
        assert len(registry.list_analyzers()) == 0


class TestPluginDiscovery:
    """Tests for plugin discovery."""
    
    def test_discover_plugins(self):
        """Test discovering plugins from directory."""
        registry = AnalyzerRegistry()
        initial_count = len(registry.list_analyzers())
        
        plugin_dir = get_test_plugin_dir()
        loaded_count = registry.discover_plugins(str(plugin_dir))
        
        assert loaded_count >= 2  # Should load at least 2 test plugins
        assert len(registry.list_analyzers()) == initial_count + loaded_count
    
    def test_discover_plugins_loads_custom_analyzer(self):
        """Test that custom analyzer is loaded."""
        registry = AnalyzerRegistry()
        
        plugin_dir = get_test_plugin_dir()
        registry.discover_plugins(str(plugin_dir))
        
        assert registry.has_analyzer("test_custom")
        analyzer_class = registry.get_analyzer("test_custom")
        assert analyzer_class.__name__ == "TestCustomAnalyzer"
    
    def test_discover_plugins_loads_resource_analyzer(self):
        """Test that resource analyzer is loaded."""
        registry = AnalyzerRegistry()
        
        plugin_dir = get_test_plugin_dir()
        registry.discover_plugins(str(plugin_dir))
        
        assert registry.has_analyzer("test_resource")
        analyzer_class = registry.get_analyzer("test_resource")
        assert analyzer_class.__name__ == "TestResourceAnalyzer"
    
    def test_discover_nonexistent_directory(self):
        """Test discovering from non-existent directory."""
        registry = AnalyzerRegistry()
        
        loaded_count = registry.discover_plugins("/nonexistent/path")
        assert loaded_count == 0
    
    def test_discover_empty_directory(self, tmp_path):
        """Test discovering from empty directory."""
        registry = AnalyzerRegistry()
        
        loaded_count = registry.discover_plugins(str(tmp_path))
        assert loaded_count == 0
    
    def test_discover_skips_private_files(self, tmp_path):
        """Test that private files are skipped."""
        registry = AnalyzerRegistry()
        
        # Create a private file
        private_file = tmp_path / "_private.py"
        private_file.write_text("# Private file")
        
        loaded_count = registry.discover_plugins(str(tmp_path))
        assert loaded_count == 0


class TestAnalyzerValidation:
    """Tests for analyzer validation."""
    
    def test_validate_complete_analyzer(self):
        """Test validation of complete analyzer."""
        registry = AnalyzerRegistry()
        
        is_valid = registry.validate_analyzer(StructuralAnalyzer)
        assert is_valid is True
    
    def test_validate_missing_methods(self):
        """Test validation fails for missing methods."""
        registry = AnalyzerRegistry()
        
        class IncompleteAnalyzer(Analyzer):
            # Missing analyze() method
            def get_requirements(self):
                return []
        
        is_valid = registry.validate_analyzer(IncompleteAnalyzer)
        assert is_valid is False
    
    def test_validate_missing_properties(self):
        """Test validation fails for missing properties."""
        registry = AnalyzerRegistry()
        
        class NoPropertiesAnalyzer(Analyzer):
            def analyze(self, sentences):
                return {}
            
            def get_requirements(self):
                return []
            
            def can_run(self):
                return True, None
            # Missing name and version properties
        
        is_valid = registry.validate_analyzer(NoPropertiesAnalyzer)
        assert is_valid is False
    
    def test_validate_non_class(self):
        """Test validation fails for non-class."""
        registry = AnalyzerRegistry()
        
        is_valid = registry.validate_analyzer("not a class")
        assert is_valid is False
    
    def test_validate_non_analyzer_subclass(self):
        """Test validation fails for non-Analyzer subclass."""
        registry = AnalyzerRegistry()
        
        class NotAnAnalyzer:
            pass
        
        is_valid = registry.validate_analyzer(NotAnAnalyzer)
        assert is_valid is False
    
    def test_validate_all_builtin_analyzers(self):
        """Test that all built-in analyzers are valid."""
        registry = AnalyzerRegistry()
        
        for analyzer_name in registry.list_analyzers():
            analyzer_class = registry.get_analyzer(analyzer_name)
            is_valid = registry.validate_analyzer(analyzer_class)
            assert is_valid is True, f"{analyzer_name} should be valid"


class TestPluginIntegration:
    """Tests for plugin integration with registry."""
    
    def test_plugin_can_be_instantiated(self):
        """Test that loaded plugin can be instantiated."""
        registry = AnalyzerRegistry()
        plugin_dir = get_test_plugin_dir()
        registry.discover_plugins(str(plugin_dir))
        
        analyzer_class = registry.get_analyzer("test_custom")
        analyzer = analyzer_class()
        
        assert analyzer is not None
        assert analyzer.name == "test_custom"
        assert analyzer.version == "1.0.0"
    
    def test_plugin_can_analyze(self):
        """Test that loaded plugin can perform analysis."""
        from src.langquality.data.models import Sentence
        
        registry = AnalyzerRegistry()
        plugin_dir = get_test_plugin_dir()
        registry.discover_plugins(str(plugin_dir))
        
        analyzer_class = registry.get_analyzer("test_custom")
        analyzer = analyzer_class()
        
        sentences = [
            Sentence("Test sentence one", "test", "test.csv", 1, 18, 3, {}),
            Sentence("Another test sentence", "test", "test.csv", 2, 21, 3, {}),
        ]
        
        metrics = analyzer.analyze(sentences)
        assert metrics.total_sentences == 2
        assert metrics.custom_score > 0
    
    def test_resource_plugin_requirements(self):
        """Test that resource plugin reports requirements."""
        registry = AnalyzerRegistry()
        plugin_dir = get_test_plugin_dir()
        registry.discover_plugins(str(plugin_dir))
        
        analyzer_class = registry.get_analyzer("test_resource")
        analyzer = analyzer_class()
        
        requirements = analyzer.get_requirements()
        assert "lexicon" in requirements
    
    def test_resource_plugin_can_run_check(self):
        """Test resource plugin can_run check."""
        from src.langquality.language_packs.models import (
            LanguagePack, LanguageConfig, PackMetadata
        )
        
        registry = AnalyzerRegistry()
        plugin_dir = get_test_plugin_dir()
        registry.discover_plugins(str(plugin_dir))
        
        analyzer_class = registry.get_analyzer("test_resource")
        
        # Without language pack
        analyzer1 = analyzer_class()
        can_run, reason = analyzer1.can_run()
        assert can_run is False
        assert "No language pack" in reason
        
        # With language pack but no lexicon
        pack_no_lexicon = LanguagePack(
            code="test",
            name="Test",
            config=LanguageConfig(code="test", name="Test"),
            metadata=PackMetadata(version="1.0.0", author="Test", email="test@test.com"),
            resources={}
        )
        analyzer2 = analyzer_class(language_pack=pack_no_lexicon)
        can_run, reason = analyzer2.can_run()
        assert can_run is False
        assert "lexicon" in reason
        
        # With language pack and lexicon
        pack_with_lexicon = LanguagePack(
            code="test",
            name="Test",
            config=LanguageConfig(code="test", name="Test"),
            metadata=PackMetadata(version="1.0.0", author="Test", email="test@test.com"),
            resources={"lexicon": ["word1", "word2"]}
        )
        analyzer3 = analyzer_class(language_pack=pack_with_lexicon)
        can_run, reason = analyzer3.can_run()
        assert can_run is True
        assert reason is None
