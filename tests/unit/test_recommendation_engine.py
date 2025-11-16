"""Unit tests for recommendation engine."""

from datetime import datetime

from src.langquality.recommendations.engine import RecommendationEngine
from src.langquality.recommendations.best_practices import BestPractices
from src.langquality.recommendations.models import Recommendation
from src.langquality.pipeline.results import AnalysisResults
from src.langquality.analyzers.structural import StructuralMetrics
from src.langquality.analyzers.linguistic import LinguisticMetrics
from src.langquality.analyzers.diversity import DiversityMetrics
from src.langquality.analyzers.domain import DomainMetrics
from src.langquality.analyzers.gender_bias import GenderBiasMetrics
from src.langquality.data.models import Sentence
from src.langquality.config.models import AnalysisConfig, PipelineConfig


class TestRecommendationEngine:
    """Tests for RecommendationEngine."""
    
    def test_initialization(self):
        """Test engine initialization."""
        engine = RecommendationEngine()
        
        assert engine.best_practices is not None
        assert isinstance(engine.best_practices, BestPractices)
    
    def test_initialization_with_custom_best_practices(self):
        """Test engine initialization with custom best practices."""
        bp = BestPractices()
        engine = RecommendationEngine(best_practices=bp)
        
        assert engine.best_practices is bp
    
    def test_generate_recommendations_empty_results(self):
        """Test recommendation generation with empty results."""
        engine = RecommendationEngine()
        
        config = PipelineConfig(
            analysis=AnalysisConfig(),
            input_directory="test",
            output_directory="test_output"
        )
        
        results = AnalysisResults(
            structural=None,
            linguistic=None,
            diversity=None,
            domain=None,
            gender_bias=None,
            timestamp=datetime.now(),
            config_used=config
        )
        
        recommendations = engine.generate_recommendations(results)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) == 0
    
    def test_check_length_issues_too_long(self):
        """Test detection of too-long sentences."""
        engine = RecommendationEngine()
        
        too_long_sentences = [
            Sentence("This is a very long sentence " * 5, "test", "test.csv", i, 150, 25, {})
            for i in range(1, 11)
        ]
        
        structural = StructuralMetrics(
            total_sentences=50,
            char_distribution={"mean": 50.0, "median": 48.0, "std": 10.0},
            word_distribution={"mean": 10.0, "median": 9.0, "std": 2.0},
            too_short=[],
            too_long=too_long_sentences,
            length_histogram={}
        )
        
        recommendations = engine._check_length_issues(structural)
        
        assert len(recommendations) > 0
        assert any("exceed maximum length" in r.title for r in recommendations)
        assert any(r.category == "structural" for r in recommendations)
    
    def test_check_length_issues_too_short(self):
        """Test detection of too-short sentences."""
        engine = RecommendationEngine()
        
        too_short_sentences = [
            Sentence("Hi", "test", "test.csv", i, 2, 1, {})
            for i in range(1, 6)
        ]
        
        structural = StructuralMetrics(
            total_sentences=30,
            char_distribution={"mean": 20.0, "median": 18.0, "std": 5.0},
            word_distribution={"mean": 5.0, "median": 4.0, "std": 1.0},
            too_short=too_short_sentences,
            too_long=[],
            length_histogram={}
        )
        
        recommendations = engine._check_length_issues(structural)
        
        assert len(recommendations) > 0
        assert any("below minimum length" in r.title for r in recommendations)
    
    def test_check_complexity_issues_high_readability(self):
        """Test detection of high readability score."""
        engine = RecommendationEngine()
        
        linguistic = LinguisticMetrics(
            avg_readability_score=75.0,  # Above threshold
            readability_distribution=[70.0, 75.0, 80.0],
            avg_lexical_complexity=0.3,
            jargon_detected={},
            complex_syntax_count=0,
            complex_sentences=[]
        )
        
        recommendations = engine._check_complexity_issues(linguistic)
        
        assert len(recommendations) > 0
        assert any("readability score" in r.title.lower() for r in recommendations)
    
    def test_check_complexity_issues_jargon(self):
        """Test detection of jargon."""
        engine = RecommendationEngine()
        
        linguistic = LinguisticMetrics(
            avg_readability_score=50.0,
            readability_distribution=[50.0],
            avg_lexical_complexity=0.5,
            jargon_detected={
                "test.csv:1": ["épistémologie", "paradigme"],
                "test.csv:2": ["méthodologie"]
            },
            complex_syntax_count=0,
            complex_sentences=[]
        )
        
        recommendations = engine._check_complexity_issues(linguistic)
        
        assert len(recommendations) > 0
        assert any("jargon" in r.title.lower() for r in recommendations)
    
    def test_check_diversity_issues_low_ttr(self):
        """Test detection of low TTR."""
        engine = RecommendationEngine()
        
        diversity = DiversityMetrics(
            ttr=0.3,  # Below threshold
            unique_words=300,
            total_words=1000,
            vocabulary_coverage=0.5,
            bigram_distribution={},
            trigram_distribution={},
            repetitive_ngrams=[],
            near_duplicates=[],
            sentence_starter_diversity=0.5
        )
        
        recommendations = engine._check_diversity_issues(diversity)
        
        assert len(recommendations) > 0
        assert any("vocabulary diversity" in r.title.lower() for r in recommendations)
    
    def test_check_diversity_issues_near_duplicates(self):
        """Test detection of near-duplicates."""
        engine = RecommendationEngine()
        
        s1 = Sentence("Bonjour tout le monde", "test", "test.csv", 1, 21, 4, {})
        s2 = Sentence("Bonjour tout le monde!", "test", "test.csv", 2, 22, 4, {})
        
        diversity = DiversityMetrics(
            ttr=0.7,
            unique_words=500,
            total_words=700,
            vocabulary_coverage=0.8,
            bigram_distribution={},
            trigram_distribution={},
            repetitive_ngrams=[],
            near_duplicates=[(s1, s2, 0.95)],
            sentence_starter_diversity=0.6
        )
        
        recommendations = engine._check_diversity_issues(diversity)
        
        assert len(recommendations) > 0
        assert any("duplicate" in r.title.lower() for r in recommendations)
    
    def test_check_domain_balance_underrepresented(self):
        """Test detection of underrepresented domains."""
        engine = RecommendationEngine()
        
        domain = DomainMetrics(
            domain_counts={"major": 90, "minor": 5},
            domain_percentages={"major": 0.95, "minor": 0.05},
            underrepresented=["minor"],
            overrepresented=[],
            total_domains=2
        )
        
        recommendations = engine._check_domain_balance(domain)
        
        assert len(recommendations) > 0
        assert any("underrepresented" in r.title.lower() for r in recommendations)
    
    def test_check_domain_balance_overrepresented(self):
        """Test detection of overrepresented domains."""
        engine = RecommendationEngine()
        
        domain = DomainMetrics(
            domain_counts={"dominant": 80, "minor": 20},
            domain_percentages={"dominant": 0.80, "minor": 0.20},
            underrepresented=[],
            overrepresented=["dominant"],
            total_domains=2
        )
        
        recommendations = engine._check_domain_balance(domain)
        
        assert len(recommendations) > 0
        assert any("overrepresented" in r.title.lower() for r in recommendations)
    
    def test_check_gender_bias_imbalance(self):
        """Test detection of gender imbalance."""
        engine = RecommendationEngine()
        
        gender_bias = GenderBiasMetrics(
            masculine_count=80,
            feminine_count=20,
            gender_ratio=0.25,  # F/M ratio
            stereotypes_detected=[],
            bias_score=0.3,
            total_gendered_mentions=100
        )
        
        recommendations = engine._check_gender_bias(gender_bias)
        
        assert len(recommendations) > 0
        assert any("gender imbalance" in r.title.lower() for r in recommendations)
    
    def test_check_gender_bias_stereotypes(self):
        """Test detection of gender stereotypes."""
        engine = RecommendationEngine()
        
        gender_bias = GenderBiasMetrics(
            masculine_count=50,
            feminine_count=50,
            gender_ratio=1.0,
            stereotypes_detected=[
                {
                    "stereotype_type": "gendered_profession",
                    "sentence": "Il est ingénieur",
                    "source_file": "test.csv",
                    "line_number": 1
                },
                {
                    "stereotype_type": "gendered_profession",
                    "sentence": "Elle est secrétaire",
                    "source_file": "test.csv",
                    "line_number": 2
                }
            ],
            bias_score=0.2,
            total_gendered_mentions=100
        )
        
        recommendations = engine._check_gender_bias(gender_bias)
        
        assert len(recommendations) > 0
        assert any("stereotype" in r.title.lower() for r in recommendations)
    
    def test_prioritize_recommendations(self):
        """Test recommendation prioritization."""
        engine = RecommendationEngine()
        bp = BestPractices()
        
        recommendations = [
            Recommendation(
                category="test",
                severity=bp.SEVERITY_INFO,
                title="Low priority",
                description="Test",
                priority=bp.PRIORITY_LOW
            ),
            Recommendation(
                category="test",
                severity=bp.SEVERITY_CRITICAL,
                title="High priority",
                description="Test",
                priority=bp.PRIORITY_CRITICAL
            ),
            Recommendation(
                category="test",
                severity=bp.SEVERITY_WARNING,
                title="Medium priority",
                description="Test",
                priority=bp.PRIORITY_MEDIUM
            )
        ]
        
        prioritized = engine.prioritize_recommendations(recommendations)
        
        # Should be sorted by priority
        assert prioritized[0].priority == bp.PRIORITY_CRITICAL
        assert prioritized[-1].priority == bp.PRIORITY_LOW
    
    def test_prioritize_recommendations_by_severity(self):
        """Test prioritization by severity when priority is same."""
        engine = RecommendationEngine()
        bp = BestPractices()
        
        recommendations = [
            Recommendation(
                category="test",
                severity=bp.SEVERITY_INFO,
                title="Info",
                description="Test",
                priority=bp.PRIORITY_HIGH
            ),
            Recommendation(
                category="test",
                severity=bp.SEVERITY_CRITICAL,
                title="Critical",
                description="Test",
                priority=bp.PRIORITY_HIGH
            ),
            Recommendation(
                category="test",
                severity=bp.SEVERITY_WARNING,
                title="Warning",
                description="Test",
                priority=bp.PRIORITY_HIGH
            )
        ]
        
        prioritized = engine.prioritize_recommendations(recommendations)
        
        # Within same priority, critical should come first
        assert prioritized[0].severity == bp.SEVERITY_CRITICAL
        assert prioritized[1].severity == bp.SEVERITY_WARNING
        assert prioritized[2].severity == bp.SEVERITY_INFO
    
    def test_generate_recommendations_full_analysis(self):
        """Test full recommendation generation with all metrics."""
        engine = RecommendationEngine()
        
        config = PipelineConfig(
            analysis=AnalysisConfig(),
            input_directory="test",
            output_directory="test_output"
        )
        
        structural = StructuralMetrics(
            total_sentences=100,
            char_distribution={"mean": 50.0, "median": 48.0, "std": 10.0},
            word_distribution={"mean": 25.0, "median": 24.0, "std": 5.0},
            too_short=[],
            too_long=[Sentence("Long " * 30, "test", "test.csv", 1, 180, 30, {})],
            length_histogram={}
        )
        
        linguistic = LinguisticMetrics(
            avg_readability_score=70.0,
            readability_distribution=[70.0],
            avg_lexical_complexity=0.8,
            jargon_detected={"test.csv:1": ["jargon"]},
            complex_syntax_count=5,
            complex_sentences=[]
        )
        
        diversity = DiversityMetrics(
            ttr=0.4,
            unique_words=400,
            total_words=1000,
            vocabulary_coverage=0.6,
            bigram_distribution={},
            trigram_distribution={},
            repetitive_ngrams=[],
            near_duplicates=[],
            sentence_starter_diversity=0.3
        )
        
        domain = DomainMetrics(
            domain_counts={"major": 90, "minor": 10},
            domain_percentages={"major": 0.90, "minor": 0.10},
            underrepresented=[],
            overrepresented=[],
            total_domains=2
        )
        
        gender_bias = GenderBiasMetrics(
            masculine_count=70,
            feminine_count=30,
            gender_ratio=0.43,
            stereotypes_detected=[],
            bias_score=0.2,
            total_gendered_mentions=100
        )
        
        results = AnalysisResults(
            structural=structural,
            linguistic=linguistic,
            diversity=diversity,
            domain=domain,
            gender_bias=gender_bias,
            timestamp=datetime.now(),
            config_used=config
        )
        
        recommendations = engine.generate_recommendations(results)
        
        # Should generate multiple recommendations
        assert len(recommendations) > 0
        
        # Should have recommendations from different categories
        categories = {r.category for r in recommendations}
        assert len(categories) > 1
        
        # Should be sorted by priority
        for i in range(len(recommendations) - 1):
            assert recommendations[i].priority <= recommendations[i + 1].priority


class TestRecommendationModel:
    """Tests for Recommendation data model."""
    
    def test_recommendation_creation(self):
        """Test Recommendation creation."""
        rec = Recommendation(
            category="test",
            severity="warning",
            title="Test recommendation",
            description="This is a test",
            affected_items=["item1", "item2"],
            suggested_actions=["action1", "action2"],
            priority=2
        )
        
        assert rec.category == "test"
        assert rec.severity == "warning"
        assert rec.title == "Test recommendation"
        assert rec.description == "This is a test"
        assert len(rec.affected_items) == 2
        assert len(rec.suggested_actions) == 2
        assert rec.priority == 2
    
    def test_recommendation_defaults(self):
        """Test Recommendation with default values."""
        rec = Recommendation(
            category="test",
            severity="info",
            title="Test",
            description="Test description"
        )
        
        assert rec.affected_items == []
        assert rec.suggested_actions == []
        assert rec.priority == 1
