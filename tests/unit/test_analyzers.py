"""Unit tests for analyzers."""

from src.langquality.analyzers.structural import StructuralAnalyzer, StructuralMetrics
from src.langquality.analyzers.domain import DomainAnalyzer, DomainMetrics
from src.langquality.analyzers.diversity import DiversityAnalyzer, DiversityMetrics
from src.langquality.analyzers.linguistic import LinguisticAnalyzer, LinguisticMetrics
from src.langquality.analyzers.gender_bias import GenderBiasAnalyzer, GenderBiasMetrics
from src.langquality.data.models import Sentence
from src.langquality.config.models import AnalysisConfig


class TestStructuralAnalyzer:
    """Tests for StructuralAnalyzer."""
    
    def test_analyze_basic(self):
        """Test basic structural analysis."""
        config = AnalysisConfig(min_words=3, max_words=20)
        analyzer = StructuralAnalyzer(config)
        
        sentences = [
            Sentence("Bonjour tout le monde", "test", "test.csv", 1, 21, 4, {}),
            Sentence("Cette phrase est plus longue", "test", "test.csv", 2, 29, 5, {}),
            Sentence("Court", "test", "test.csv", 3, 5, 1, {}),
        ]
        
        metrics = analyzer.analyze(sentences)
        
        assert metrics.total_sentences == 3
        assert metrics.word_distribution['min'] == 1.0
        assert metrics.word_distribution['max'] == 5.0
        assert metrics.word_distribution['mean'] > 0
    
    def test_compute_length_distribution_words(self):
        """Test word length distribution calculation."""
        config = AnalysisConfig()
        analyzer = StructuralAnalyzer(config)
        
        sentences = [
            Sentence("Un deux trois", "test", "test.csv", 1, 13, 3, {}),
            Sentence("Un deux trois quatre cinq", "test", "test.csv", 2, 25, 5, {}),
            Sentence("Un deux trois quatre", "test", "test.csv", 3, 20, 4, {}),
        ]
        
        dist = analyzer.compute_length_distribution(sentences, 'word')
        
        assert dist['min'] == 3.0
        assert dist['max'] == 5.0
        assert dist['mean'] == 4.0
        assert dist['median'] == 4.0
        assert 'std' in dist
    
    def test_compute_length_distribution_chars(self):
        """Test character length distribution calculation."""
        config = AnalysisConfig()
        analyzer = StructuralAnalyzer(config)
        
        sentences = [
            Sentence("ABC", "test", "test.csv", 1, 3, 1, {}),
            Sentence("ABCDE", "test", "test.csv", 2, 5, 1, {}),
        ]
        
        dist = analyzer.compute_length_distribution(sentences, 'char')
        
        assert dist['min'] == 3.0
        assert dist['max'] == 5.0
        assert dist['mean'] == 4.0
    
    def test_identify_outliers(self):
        """Test identification of too short and too long sentences."""
        config = AnalysisConfig(min_words=3, max_words=10)
        analyzer = StructuralAnalyzer(config)
        
        sentences = [
            Sentence("Court", "test", "test.csv", 1, 5, 1, {}),  # Too short
            Sentence("Phrase normale de longueur acceptable", "test", "test.csv", 2, 38, 5, {}),  # OK
            Sentence("Cette phrase est beaucoup trop longue et dépasse largement la limite maximale autorisée", 
                    "test", "test.csv", 3, 89, 13, {}),  # Too long
        ]
        
        too_short, too_long = analyzer.identify_outliers(sentences)
        
        assert len(too_short) == 1
        assert too_short[0].word_count == 1
        assert len(too_long) == 1
        assert too_long[0].word_count == 13
    
    def test_analyze_empty_list(self):
        """Test analysis with empty sentence list."""
        config = AnalysisConfig()
        analyzer = StructuralAnalyzer(config)
        
        metrics = analyzer.analyze([])
        
        assert metrics.total_sentences == 0
        assert metrics.char_distribution == {}
        assert metrics.word_distribution == {}
        assert metrics.too_short == []
        assert metrics.too_long == []
    
    def test_histogram_creation(self):
        """Test histogram creation."""
        config = AnalysisConfig()
        analyzer = StructuralAnalyzer(config)
        
        sentences = [
            Sentence("Un deux trois", "test", "test.csv", 1, 13, 3, {}),
            Sentence("Un deux trois quatre", "test", "test.csv", 2, 20, 4, {}),
            Sentence("Un deux trois", "test", "test.csv", 3, 13, 3, {}),
        ]
        
        metrics = analyzer.analyze(sentences)
        
        assert metrics.length_histogram[3] == 2
        assert metrics.length_histogram[4] == 1


class TestDomainAnalyzer:
    """Tests for DomainAnalyzer."""
    
    def test_analyze_basic(self):
        """Test basic domain analysis."""
        config = AnalysisConfig()
        analyzer = DomainAnalyzer(config)
        
        sentences = [
            Sentence("Phrase santé", "health", "health.csv", 1, 12, 2, {}),
            Sentence("Phrase éducation", "education", "education.csv", 1, 16, 2, {}),
            Sentence("Autre phrase santé", "health", "health.csv", 2, 18, 3, {}),
        ]
        
        metrics = analyzer.analyze(sentences)
        
        assert metrics.total_domains == 2
        assert metrics.domain_counts['health'] == 2
        assert metrics.domain_counts['education'] == 1
    
    def test_compute_domain_distribution(self):
        """Test domain distribution calculation."""
        config = AnalysisConfig()
        analyzer = DomainAnalyzer(config)
        
        sentences = [
            Sentence("Test", "domain1", "d1.csv", 1, 4, 1, {}),
            Sentence("Test", "domain1", "d1.csv", 2, 4, 1, {}),
            Sentence("Test", "domain2", "d2.csv", 1, 4, 1, {}),
        ]
        
        distribution = analyzer.compute_domain_distribution(sentences)
        
        assert distribution['domain1'] == 2
        assert distribution['domain2'] == 1
    
    def test_identify_underrepresented_domains(self):
        """Test identification of underrepresented domains."""
        config = AnalysisConfig(min_domain_representation=0.10)
        analyzer = DomainAnalyzer(config)
        
        sentences = [
            Sentence("Test", "major", "major.csv", i, 4, 1, {}) for i in range(1, 91)
        ] + [
            Sentence("Test", "minor", "minor.csv", i, 4, 1, {}) for i in range(1, 11)
        ]
        
        metrics = analyzer.analyze(sentences)
        
        assert 'minor' in metrics.underrepresented
        assert 'major' not in metrics.underrepresented
    
    def test_identify_overrepresented_domains(self):
        """Test identification of overrepresented domains."""
        config = AnalysisConfig(max_domain_representation=0.30)
        analyzer = DomainAnalyzer(config)
        
        sentences = [
            Sentence("Test", "dominant", "dominant.csv", i, 4, 1, {}) for i in range(1, 41)
        ] + [
            Sentence("Test", "minor", "minor.csv", i, 4, 1, {}) for i in range(1, 11)
        ]
        
        metrics = analyzer.analyze(sentences)
        
        assert 'dominant' in metrics.overrepresented
        assert 'minor' not in metrics.overrepresented


class TestDiversityAnalyzer:
    """Tests for DiversityAnalyzer."""
    
    def test_analyze_basic(self):
        """Test basic diversity analysis."""
        config = AnalysisConfig()
        analyzer = DiversityAnalyzer(config)
        
        sentences = [
            Sentence("Bonjour tout le monde", "test", "test.csv", 1, 21, 4, {}),
            Sentence("Le monde est grand", "test", "test.csv", 2, 18, 4, {}),
        ]
        
        metrics = analyzer.analyze(sentences)
        
        assert metrics.total_words > 0
        assert metrics.unique_words > 0
        assert 0 <= metrics.ttr <= 1
    
    def test_compute_ttr(self):
        """Test Type-Token Ratio calculation."""
        config = AnalysisConfig()
        analyzer = DiversityAnalyzer(config)
        
        sentences = [
            Sentence("chat chat chat", "test", "test.csv", 1, 14, 3, {}),
            Sentence("chien oiseau poisson", "test", "test.csv", 2, 20, 3, {}),
        ]
        
        ttr = analyzer.compute_ttr(sentences)
        
        # 4 unique words (chat, chien, oiseau, poisson) / 6 total words
        assert ttr == 4.0 / 6.0
    
    def test_extract_ngrams(self):
        """Test n-gram extraction."""
        config = AnalysisConfig()
        analyzer = DiversityAnalyzer(config)
        
        sentences = [
            Sentence("le chat noir", "test", "test.csv", 1, 13, 3, {}),
            Sentence("le chien blanc", "test", "test.csv", 2, 14, 3, {}),
        ]
        
        bigrams = analyzer.extract_ngrams(sentences, 2)
        
        assert ('le', 'chat') in bigrams
        assert ('le', 'chien') in bigrams
        assert bigrams[('le', 'chat')] == 1
    
    def test_detect_near_duplicates(self):
        """Test near-duplicate detection."""
        config = AnalysisConfig()
        analyzer = DiversityAnalyzer(config)
        
        sentences = [
            Sentence("Bonjour tout le monde", "test", "test.csv", 1, 21, 4, {}),
            Sentence("Bonjour tout le monde!", "test", "test.csv", 2, 22, 4, {}),
            Sentence("Phrase complètement différente", "test", "test.csv", 3, 30, 3, {}),
        ]
        
        duplicates = analyzer.detect_near_duplicates(sentences)
        
        # Should find the two similar sentences
        assert len(duplicates) > 0
        assert duplicates[0][2] > 0.8  # High similarity


class TestLinguisticAnalyzer:
    """Tests for LinguisticAnalyzer."""
    
    def test_analyze_basic(self):
        """Test basic linguistic analysis."""
        config = AnalysisConfig()
        analyzer = LinguisticAnalyzer(config)
        
        sentences = [
            Sentence("Bonjour, comment allez-vous?", "test", "test.csv", 1, 28, 4, {}),
            Sentence("Cette phrase est simple.", "test", "test.csv", 2, 24, 4, {}),
        ]
        
        metrics = analyzer.analyze(sentences)
        
        assert metrics.avg_readability_score >= 0
        assert metrics.avg_lexical_complexity >= 0
        assert len(metrics.readability_distribution) == 2
    
    def test_compute_readability_score(self):
        """Test readability score calculation."""
        config = AnalysisConfig()
        analyzer = LinguisticAnalyzer(config)
        
        sentence = Sentence("Le chat dort.", "test", "test.csv", 1, 13, 3, {})
        
        score = analyzer.compute_readability_score(sentence)
        
        # Should return a numeric score
        assert isinstance(score, (int, float))
        assert score >= 0
    
    def test_compute_lexical_complexity(self):
        """Test lexical complexity calculation."""
        config = AnalysisConfig()
        analyzer = LinguisticAnalyzer(config)
        
        # Simple sentence with common words
        simple = Sentence("Le chat est noir", "test", "test.csv", 1, 16, 4, {})
        simple_score = analyzer.compute_lexical_complexity(simple)
        
        # Complex sentence with rare words
        complex_sent = Sentence("L'épistémologie contemporaine", "test", "test.csv", 2, 29, 2, {})
        complex_score = analyzer.compute_lexical_complexity(complex_sent)
        
        # Complex sentence should have higher complexity
        assert complex_score >= simple_score
    
    def test_detect_jargon(self):
        """Test jargon detection."""
        config = AnalysisConfig(jargon_terms=["épistémologie", "paradigme"])
        analyzer = LinguisticAnalyzer(config)
        
        sentence = Sentence("L'épistémologie est complexe", "test", "test.csv", 1, 28, 3, {})
        
        jargon = analyzer.detect_jargon(sentence)
        
        assert len(jargon) > 0
        assert any("épistémologie" in term.lower() for term in jargon)


class TestGenderBiasAnalyzer:
    """Tests for GenderBiasAnalyzer."""
    
    def test_analyze_basic(self):
        """Test basic gender bias analysis."""
        analyzer = GenderBiasAnalyzer()
        
        sentences = [
            Sentence("Il est médecin", "test", "test.csv", 1, 14, 3, {}),
            Sentence("Elle est infirmière", "test", "test.csv", 2, 19, 3, {}),
        ]
        
        metrics = analyzer.analyze(sentences)
        
        assert metrics.masculine_count > 0
        assert metrics.feminine_count > 0
        assert 0 <= metrics.bias_score <= 1
    
    def test_count_gender_mentions(self):
        """Test gender mention counting."""
        analyzer = GenderBiasAnalyzer()
        
        sentences = [
            Sentence("Il travaille avec lui", "test", "test.csv", 1, 21, 4, {}),
            Sentence("Elle parle avec elle", "test", "test.csv", 2, 20, 4, {}),
        ]
        
        counts = analyzer.count_gender_mentions(sentences)
        
        assert counts['masculine'] > 0
        assert counts['feminine'] > 0
    
    def test_compute_gender_ratio(self):
        """Test gender ratio calculation."""
        analyzer = GenderBiasAnalyzer()
        
        counts = {'masculine': 60, 'feminine': 40}
        ratio = analyzer.compute_gender_ratio(counts)
        
        # Ratio should be feminine/masculine
        assert ratio == 40.0 / 60.0
    
    def test_compute_gender_ratio_zero_masculine(self):
        """Test gender ratio with zero masculine mentions."""
        analyzer = GenderBiasAnalyzer()
        
        counts = {'masculine': 0, 'feminine': 10}
        ratio = analyzer.compute_gender_ratio(counts)
        
        # Should handle division by zero
        assert ratio >= 0
    
    def test_detect_stereotypes(self):
        """Test stereotype detection."""
        analyzer = GenderBiasAnalyzer()
        
        sentences = [
            Sentence("Il est ingénieur", "test", "test.csv", 1, 16, 3, {}),
            Sentence("Elle est secrétaire", "test", "test.csv", 2, 19, 3, {}),
        ]
        
        stereotypes = analyzer.detect_stereotypes(sentences)
        
        # Should detect gendered profession associations
        assert isinstance(stereotypes, list)
