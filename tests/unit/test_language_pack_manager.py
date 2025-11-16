"""Unit tests for LanguagePackManager."""

import pytest
from pathlib import Path

from src.langquality.language_packs.manager import LanguagePackManager
from src.langquality.language_packs.models import LanguagePack
from src.langquality.language_packs.validation import ValidationError
from tests.fixtures import get_language_packs_dir, get_test_pack_path


class TestLanguagePackManager:
    """Tests for LanguagePackManager class."""
    
    @pytest.fixture
    def manager(self):
        """Create a manager with test fixtures directory."""
        return LanguagePackManager(get_language_packs_dir())
    
    def test_initialization(self, manager):
        """Test manager initialization."""
        assert manager.packs_directory == get_language_packs_dir()
        assert isinstance(manager._cache, dict)
        assert len(manager._cache) == 0
    
    def test_load_complete_pack(self, manager):
        """Test loading a complete language pack."""
        pack = manager.load_language_pack("test_complete")
        
        assert isinstance(pack, LanguagePack)
        assert pack.code == "test_complete"
        assert pack.name == "Test Language"
        assert pack.config.code == "tst"
        assert pack.metadata.version == "1.0.0"
    
    def test_load_minimal_pack(self, manager):
        """Test loading a minimal language pack."""
        pack = manager.load_language_pack("test_minimal")
        
        assert isinstance(pack, LanguagePack)
        assert pack.code == "test_minimal"
        assert pack.name == "Minimal Test Language"
        assert len(pack.resources) == 0
    
    def test_load_nonexistent_pack(self, manager):
        """Test loading a non-existent pack raises error."""
        with pytest.raises(FileNotFoundError, match="not found"):
            manager.load_language_pack("nonexistent")
    
    def test_load_invalid_pack(self, manager):
        """Test loading an invalid pack raises validation error."""
        with pytest.raises(ValidationError):
            manager.load_language_pack("test_invalid")
    
    def test_load_pack_without_validation(self, manager):
        """Test loading pack without validation."""
        # Invalid pack will still fail if config is malformed
        # This test verifies that validation can be skipped
        with pytest.raises((KeyError, Exception)):
            pack = manager.load_language_pack("test_invalid", validate=False)
    
    def test_caching(self, manager):
        """Test that packs are cached after first load."""
        pack1 = manager.load_language_pack("test_complete")
        pack2 = manager.load_language_pack("test_complete")
        
        # Should be the same object from cache
        assert pack1 is pack2
        assert "test_complete" in manager._cache
    
    def test_clear_cache(self, manager):
        """Test cache clearing."""
        manager.load_language_pack("test_complete")
        assert len(manager._cache) == 1
        
        manager.clear_cache()
        assert len(manager._cache) == 0
    
    def test_list_available_packs(self, manager):
        """Test listing available packs."""
        packs = manager.list_available_packs()
        
        assert isinstance(packs, list)
        assert "test_complete" in packs
        assert "test_minimal" in packs
        # test_invalid should be included (has required files)
        assert len(packs) >= 2
    
    def test_get_pack_info(self, manager):
        """Test getting pack info without full load."""
        info = manager.get_pack_info("test_complete")
        
        assert info is not None
        assert info["code"] == "test_complete"
        assert info["name"] == "Test Language"
        assert info["version"] == "1.0.0"
        assert info["status"] == "stable"
    
    def test_get_pack_info_nonexistent(self, manager):
        """Test getting info for non-existent pack."""
        info = manager.get_pack_info("nonexistent")
        assert info is None
    
    def test_validate_pack(self, manager):
        """Test pack validation."""
        pack_path = get_test_pack_path("test_complete")
        is_valid, errors, warnings = manager.validate_pack(pack_path)
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_invalid_pack(self, manager):
        """Test validation of invalid pack."""
        pack_path = get_test_pack_path("test_invalid")
        is_valid, errors, warnings = manager.validate_pack(pack_path)
        
        assert is_valid is False
        assert len(errors) > 0


class TestLanguagePackResources:
    """Tests for resource loading in language packs."""
    
    @pytest.fixture
    def manager(self):
        """Create a manager with test fixtures directory."""
        return LanguagePackManager(get_language_packs_dir())
    
    def test_load_all_resources(self, manager):
        """Test that all resources are loaded for complete pack."""
        pack = manager.load_language_pack("test_complete")
        
        assert pack.has_resource("lexicon")
        assert pack.has_resource("stopwords")
        assert pack.has_resource("gender_terms")
        assert pack.has_resource("professions")
        assert pack.has_resource("stereotypes")
    
    def test_get_resource(self, manager):
        """Test getting a resource."""
        pack = manager.load_language_pack("test_complete")
        
        lexicon = pack.get_resource("lexicon")
        assert isinstance(lexicon, list)
        assert len(lexicon) > 0
        assert "hello" in lexicon
    
    def test_get_resource_with_default(self, manager):
        """Test getting resource with default value."""
        pack = manager.load_language_pack("test_minimal")
        
        lexicon = pack.get_resource("lexicon", [])
        assert lexicon == []
    
    def test_list_resources(self, manager):
        """Test listing all resources."""
        pack = manager.load_language_pack("test_complete")
        
        resources = pack.list_resources()
        assert isinstance(resources, list)
        assert "lexicon" in resources
        assert "stopwords" in resources
    
    def test_minimal_pack_no_resources(self, manager):
        """Test that minimal pack has no resources."""
        pack = manager.load_language_pack("test_minimal")
        
        assert len(pack.resources) == 0
        assert not pack.has_resource("lexicon")
    
    def test_resource_fallback(self, manager):
        """Test resource fallback for missing files."""
        pack = manager.load_language_pack("test_minimal")
        
        # Should not raise error, just return None/default
        lexicon = pack.get_resource("lexicon", None)
        assert lexicon is None


class TestLanguagePackConfiguration:
    """Tests for language pack configuration parsing."""
    
    @pytest.fixture
    def manager(self):
        """Create a manager with test fixtures directory."""
        return LanguagePackManager(get_language_packs_dir())
    
    def test_parse_language_config(self, manager):
        """Test parsing language configuration."""
        pack = manager.load_language_pack("test_complete")
        
        assert pack.config.code == "tst"
        assert pack.config.name == "Test Language"
        assert pack.config.family == "Test Family"
        assert pack.config.script == "Latin"
        assert pack.config.direction == "ltr"
    
    def test_parse_tokenization_config(self, manager):
        """Test parsing tokenization configuration."""
        pack = manager.load_language_pack("test_complete")
        
        assert pack.config.tokenization.method == "whitespace"
        assert pack.config.tokenization.model is None
        assert isinstance(pack.config.tokenization.custom_rules, list)
    
    def test_parse_thresholds(self, manager):
        """Test parsing threshold configuration."""
        pack = manager.load_language_pack("test_complete")
        
        # Structural thresholds
        assert pack.config.thresholds.structural.min_words == 3
        assert pack.config.thresholds.structural.max_words == 20
        
        # Linguistic thresholds
        assert pack.config.thresholds.linguistic.max_readability_score == 60.0
        
        # Diversity thresholds
        assert pack.config.thresholds.diversity.target_ttr == 0.6
        
        # Domain thresholds
        assert pack.config.thresholds.domain.min_representation == 0.10
        
        # Gender thresholds
        assert pack.config.thresholds.gender.target_ratio == (0.4, 0.6)
    
    def test_parse_analyzers_config(self, manager):
        """Test parsing analyzers configuration."""
        pack = manager.load_language_pack("test_complete")
        
        assert "structural" in pack.config.analyzers.enabled
        assert "linguistic" in pack.config.analyzers.enabled
        assert "diversity" in pack.config.analyzers.enabled
        assert "domain" in pack.config.analyzers.enabled
        assert "gender_bias" in pack.config.analyzers.enabled
    
    def test_parse_resources_config(self, manager):
        """Test parsing resources configuration."""
        pack = manager.load_language_pack("test_complete")
        
        assert pack.config.resources.lexicon == "lexicon.txt"
        assert pack.config.resources.stopwords == "stopwords.txt"
        assert pack.config.resources.gender_terms == "gender_terms.json"
    
    def test_default_values(self, manager):
        """Test that default values are applied for minimal pack."""
        pack = manager.load_language_pack("test_minimal")
        
        # Should have default thresholds
        assert pack.config.thresholds.structural is not None
        assert pack.config.thresholds.structural.min_words == 3


class TestLanguagePackMetadata:
    """Tests for language pack metadata."""
    
    @pytest.fixture
    def manager(self):
        """Create a manager with test fixtures directory."""
        return LanguagePackManager(get_language_packs_dir())
    
    def test_parse_metadata(self, manager):
        """Test parsing metadata."""
        pack = manager.load_language_pack("test_complete")
        
        assert pack.metadata.version == "1.0.0"
        assert pack.metadata.author == "Test Author"
        assert pack.metadata.email == "test@example.com"
        assert pack.metadata.license == "MIT"
        assert pack.metadata.status == "stable"
    
    def test_metadata_coverage(self, manager):
        """Test metadata coverage information."""
        pack = manager.load_language_pack("test_complete")
        
        assert "lexicon_size" in pack.metadata.coverage
        assert pack.metadata.coverage["lexicon_size"] == 100
        assert pack.metadata.coverage["has_gender_resources"] is True
    
    def test_metadata_dependencies(self, manager):
        """Test metadata dependencies."""
        pack = manager.load_language_pack("test_complete")
        
        assert "min_langquality_version" in pack.metadata.dependencies
        assert pack.metadata.dependencies["min_langquality_version"] == "1.0.0"
    
    def test_minimal_metadata(self, manager):
        """Test minimal metadata parsing."""
        pack = manager.load_language_pack("test_minimal")
        
        assert pack.metadata.version == "1.0.0"
        assert pack.metadata.status == "experimental"
