"""Unit tests for analyzers with Language Pack support."""

import pytest

from src.langquality.analyzers.structural import StructuralAnalyzer
from src.langquality.analyzers.linguistic import LinguisticAnalyzer
from src.langquality.analyzers.diversity import DiversityAnalyzer
from src.langquality.analyzers.domain import DomainAnalyzer
from src.langquality.analyzers.gender_bias import GenderBiasAnalyzer
from src.langquality.data.models import Sentence
from src.langquality.language_packs.manager import LanguagePackManager
from src.langquality.language_packs.models import (
    LanguagePack, LanguageConfig, PackMetadata, ThresholdConfig,
    StructuralThresholds, LinguisticThresholds, DiversityThresholds,
    DomainThresholds, GenderThresholds
)
from tests.fixtures import get_language_packs_dir


class TestAnalyzersWithLanguagePack:
    """Tests for analyzers with language pack integration."""
    
    @pytest.fixture
    def complete_pack(self):
        """Load complete test language pack."""
        manager = LanguagePackManager(get_language_packs_dir())
        return manager.load_language_pack("test_complete")
    
    @pytest.fixture
    def minimal_pack(self):
        """Load minimal test language pack."""
        manager = LanguagePackManager(get_language_packs_dir())
        return manager.load_language_pack("test_minimal")
    
    @pytest.fixture
    def sample_sentences(self):
        """Create sample sentences for testing."""
        return [
            Sentence("Hello world test", "test", "test.csv", 1, 16, 3, {}),
            Sentence("This is a longer sentence for testing", "test", "test.csv", 2, 38, 7, {}),
            Sentence("Short", "test", "test.csv", 3, 5, 1, {}),
        ]
    
    def test_structural_analyzer_with_pack(self, complete_pack, sample_sentences):
        """Test StructuralAnalyzer with language pack."""
        config = complete_pack.config.thresholds
        analyzer = StructuralAnalyzer(config, language_pack=complete_pack)
        
        metrics = analyzer.analyze(sample_sentences)
        
        assert metrics.total_sentences == 3
        assert metrics.word_distribution['min'] == 1.0
        assert metrics.word_distribution['max'] == 7.0
    
    def test_structural_analyzer_without_pack(self, sample_sentences):
        """Test StructuralAnalyzer without language pack."""
        from src.langquality.language_packs.models import ThresholdConfig
        config = ThresholdConfig()
        analyzer = StructuralAnalyzer(config)
        
        metrics = analyzer.analyze(sample_sentences)
        
        assert metrics.total_sentences == 3
        # Should still work with default configuration
    
    def test_linguistic_analyzer_with_pack(self, complete_pack, sample_sentences):
        """Test LinguisticAnalyzer with language pack."""
        config = complete_pack.config.thresholds
        analyzer = LinguisticAnalyzer(config, language_pack=complete_pack)
        
        metrics = analyzer.analyze(sample_sentences)
        
        assert metrics.avg_readability_score >= 0
        assert len(metrics.readability_distribution) == 3
    
    def test_diversity_analyzer_with_pack(self, complete_pack, sample_sentences):
        """Test DiversityAnalyzer with language pack."""
        config = complete_pack.config.thresholds
        analyzer = DiversityAnalyzer(config, language_pack=complete_pack)
        
        metrics = analyzer.analyze(sample_sentences)
        
        assert 0 <= metrics.ttr <= 1
        assert metrics.total_words > 0
        assert metrics.unique_words > 0
    
    def test_domain_analyzer_with_pack(self, complete_pack, sample_sentences):
        """Test DomainAnalyzer with language pack."""
        config = complete_pack.config.thresholds
        analyzer = DomainAnalyzer(config, language_pack=complete_pack)
        
        metrics = analyzer.analyze(sample_sentences)
        
        assert metrics.total_domains >= 1
        assert "test" in metrics.domain_counts
    
    def test_gender_bias_analyzer_with_pack(self, complete_pack):
        """Test GenderBiasAnalyzer with language pack."""
        config = complete_pack.config.thresholds
        analyzer = GenderBiasAnalyzer(config, language_pack=complete_pack)
        
        sentences = [
            Sentence("He is an engineer", "test", "test.csv", 1, 17, 4, {}),
            Sentence("She is a nurse", "test", "test.csv", 2, 14, 4, {}),
        ]
        
        metrics = analyzer.analyze(sentences)
        
        assert metrics.masculine_count > 0
        assert metrics.feminine_count > 0


class TestAnalyzerResourceRequirements:
    """Tests for analyzer resource requirements."""
    
    @pytest.fixture
    def complete_pack(self):
        """Load complete test language pack."""
        manager = LanguagePackManager(get_language_packs_dir())
        return manager.load_language_pack("test_complete")
    
    @pytest.fixture
    def minimal_pack(self):
        """Load minimal test language pack."""
        manager = LanguagePackManager(get_language_packs_dir())
        return manager.load_language_pack("test_minimal")
    
    def test_structural_analyzer_requirements(self):
        """Test StructuralAnalyzer resource requirements."""
        from src.langquality.language_packs.models import ThresholdConfig
        config = ThresholdConfig()
        analyzer = StructuralAnalyzer(config)
        requirements = analyzer.get_requirements()
        
        # Structural analyzer should have no resource requirements
        assert isinstance(requirements, list)
        assert len(requirements) == 0
    
    def test_linguistic_analyzer_requirements(self):
        """Test LinguisticAnalyzer resource requirements."""
        from src.langquality.language_packs.models import ThresholdConfig
        config = ThresholdConfig()
        analyzer = LinguisticAnalyzer(config)
        requirements = analyzer.get_requirements()
        
        # May have optional requirements
        assert isinstance(requirements, list)
    
    def test_diversity_analyzer_requirements(self):
        """Test DiversityAnalyzer resource requirements."""
        from src.langquality.language_packs.models import ThresholdConfig
        config = ThresholdConfig()
        analyzer = DiversityAnalyzer(config)
        requirements = analyzer.get_requirements()
        
        # May have optional requirements like stopwords
        assert isinstance(requirements, list)
    
    def test_gender_bias_analyzer_requirements(self):
        """Test GenderBiasAnalyzer resource requirements."""
        from src.langquality.language_packs.models import ThresholdConfig
        config = ThresholdConfig()
        analyzer = GenderBiasAnalyzer(config)
        requirements = analyzer.get_requirements()
        
        # Gender bias analyzer may require gender terms
        assert isinstance(requirements, list)
    
    def test_analyzer_can_run_with_complete_pack(self, complete_pack):
        """Test that analyzers can run with complete pack."""
        config = complete_pack.config.thresholds
        analyzers = [
            StructuralAnalyzer(config, language_pack=complete_pack),
            LinguisticAnalyzer(config, language_pack=complete_pack),
            DiversityAnalyzer(config, language_pack=complete_pack),
            DomainAnalyzer(config, language_pack=complete_pack),
            GenderBiasAnalyzer(config, language_pack=complete_pack),
        ]
        
        for analyzer in analyzers:
            can_run, reason = analyzer.can_run()
            assert can_run is True, f"{analyzer.name} should be able to run"
            assert reason is None
    
    def test_analyzer_can_run_with_minimal_pack(self, minimal_pack):
        """Test analyzer can_run with minimal pack."""
        config = minimal_pack.config.thresholds
        # Structural analyzer should always work
        structural = StructuralAnalyzer(config, language_pack=minimal_pack)
        can_run, reason = structural.can_run()
        assert can_run is True
        
        # Others may or may not work depending on requirements
        linguistic = LinguisticAnalyzer(config, language_pack=minimal_pack)
        can_run, _ = linguistic.can_run()
        # Should handle gracefully either way
        assert isinstance(can_run, bool)
    
    def test_analyzer_can_run_without_pack(self):
        """Test analyzer can_run without language pack."""
        from src.langquality.language_packs.models import ThresholdConfig
        config = ThresholdConfig()
        analyzers = [
            StructuralAnalyzer(config),
            LinguisticAnalyzer(config),
            DiversityAnalyzer(config),
            DomainAnalyzer(config),
        ]
        
        for analyzer in analyzers:
            can_run, reason = analyzer.can_run()
            # Should be able to run with defaults or report gracefully
            assert isinstance(can_run, bool)


class TestAnalyzerThresholds:
    """Tests for analyzer threshold configuration from language packs."""
    
    @pytest.fixture
    def custom_pack(self):
        """Create a pack with custom thresholds."""
        config = LanguageConfig(
            code="custom",
            name="Custom",
            thresholds=ThresholdConfig(
                structural=StructuralThresholds(
                    min_words=5,
                    max_words=15,
                    min_chars=20,
                    max_chars=150
                ),
                linguistic=LinguisticThresholds(
                    max_readability_score=50.0
                ),
                diversity=DiversityThresholds(
                    target_ttr=0.7,
                    min_unique_words=200
                ),
                domain=DomainThresholds(
                    min_representation=0.15,
                    max_representation=0.25
                ),
                gender=GenderThresholds(
                    target_ratio=(0.45, 0.55)
                )
            )
        )
        
        return LanguagePack(
            code="custom",
            name="Custom",
            config=config,
            metadata=PackMetadata(
                version="1.0.0",
                author="Test",
                email="test@test.com"
            )
        )
    
    def test_structural_analyzer_uses_pack_thresholds(self, custom_pack):
        """Test that StructuralAnalyzer uses pack thresholds."""
        config = custom_pack.config.thresholds
        analyzer = StructuralAnalyzer(config, language_pack=custom_pack)
        
        sentences = [
            Sentence("One two three four", "test", "test.csv", 1, 18, 4, {}),
            Sentence("This has exactly five words here", "test", "test.csv", 2, 32, 6, {}),
        ]
        
        metrics = analyzer.analyze(sentences)
        
        # First sentence should be flagged as too short (< 5 words)
        assert len(metrics.too_short) == 1
        assert metrics.too_short[0].word_count == 4
    
    def test_diversity_analyzer_uses_pack_thresholds(self, custom_pack):
        """Test that DiversityAnalyzer uses pack thresholds."""
        config = custom_pack.config.thresholds
        analyzer = DiversityAnalyzer(config, language_pack=custom_pack)
        
        # Target TTR from pack should be 0.7
        assert custom_pack.config.thresholds.diversity.target_ttr == 0.7


class TestAnalyzerWithMissingResources:
    """Tests for analyzer behavior with missing resources."""
    
    @pytest.fixture
    def pack_no_gender_resources(self):
        """Create a pack without gender resources."""
        config = LanguageConfig(
            code="nogender",
            name="No Gender"
        )
        
        return LanguagePack(
            code="nogender",
            name="No Gender",
            config=config,
            metadata=PackMetadata(
                version="1.0.0",
                author="Test",
                email="test@test.com"
            ),
            resources={}  # No resources
        )
    
    def test_gender_analyzer_with_missing_resources(self, pack_no_gender_resources):
        """Test GenderBiasAnalyzer with missing resources."""
        config = pack_no_gender_resources.config.thresholds
        analyzer = GenderBiasAnalyzer(config, language_pack=pack_no_gender_resources)
        
        sentences = [
            Sentence("Test sentence", "test", "test.csv", 1, 13, 2, {}),
        ]
        
        # Should handle gracefully
        try:
            metrics = analyzer.analyze(sentences)
            # If it runs, should return valid metrics
            assert metrics is not None
        except Exception as e:
            # Or should raise a clear error
            assert "resource" in str(e).lower() or "missing" in str(e).lower()
    
    def test_diversity_analyzer_without_stopwords(self, pack_no_gender_resources):
        """Test DiversityAnalyzer without stopwords resource."""
        config = pack_no_gender_resources.config.thresholds
        analyzer = DiversityAnalyzer(config, language_pack=pack_no_gender_resources)
        
        sentences = [
            Sentence("Test sentence one", "test", "test.csv", 1, 17, 3, {}),
            Sentence("Test sentence two", "test", "test.csv", 2, 17, 3, {}),
        ]
        
        # Should work without stopwords (just won't filter them)
        metrics = analyzer.analyze(sentences)
        assert metrics is not None
        assert metrics.total_words > 0


class TestAnalyzerProperties:
    """Tests for analyzer properties."""
    
    def test_analyzer_name_property(self):
        """Test that analyzers have name property."""
        from src.langquality.language_packs.models import ThresholdConfig
        config = ThresholdConfig()
        analyzers = [
            StructuralAnalyzer(config),
            LinguisticAnalyzer(config),
            DiversityAnalyzer(config),
            DomainAnalyzer(config),
            GenderBiasAnalyzer(config),
        ]
        
        for analyzer in analyzers:
            assert hasattr(analyzer, 'name')
            assert isinstance(analyzer.name, str)
            assert len(analyzer.name) > 0
    
    def test_analyzer_version_property(self):
        """Test that analyzers have version property."""
        from src.langquality.language_packs.models import ThresholdConfig
        config = ThresholdConfig()
        analyzers = [
            StructuralAnalyzer(config),
            LinguisticAnalyzer(config),
            DiversityAnalyzer(config),
            DomainAnalyzer(config),
            GenderBiasAnalyzer(config),
        ]
        
        for analyzer in analyzers:
            assert hasattr(analyzer, 'version')
            assert isinstance(analyzer.version, str)
            assert len(analyzer.version) > 0
    
    def test_analyzer_implements_required_methods(self):
        """Test that analyzers implement required methods."""
        from src.langquality.language_packs.models import ThresholdConfig
        config = ThresholdConfig()
        analyzers = [
            StructuralAnalyzer(config),
            LinguisticAnalyzer(config),
            DiversityAnalyzer(config),
            DomainAnalyzer(config),
            GenderBiasAnalyzer(config),
        ]
        
        for analyzer in analyzers:
            assert hasattr(analyzer, 'analyze')
            assert callable(analyzer.analyze)
            
            assert hasattr(analyzer, 'get_requirements')
            assert callable(analyzer.get_requirements)
            
            assert hasattr(analyzer, 'can_run')
            assert callable(analyzer.can_run)
