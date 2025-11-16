"""Structural analyzer for sentence length and distribution metrics."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import statistics

from .base import Analyzer
from ..data.models import Sentence


@dataclass
class StructuralMetrics:
    """Metrics for structural analysis of sentences.
    
    Attributes:
        total_sentences: Total number of sentences analyzed
        char_distribution: Statistical distribution of character counts
        word_distribution: Statistical distribution of word counts
        too_short: List of sentences below minimum word threshold
        too_long: List of sentences above maximum word threshold
        length_histogram: Frequency distribution of word counts
    """
    total_sentences: int
    char_distribution: Dict[str, float]
    word_distribution: Dict[str, float]
    too_short: List[Sentence]
    too_long: List[Sentence]
    length_histogram: Dict[int, int] = field(default_factory=dict)


class StructuralAnalyzer(Analyzer):
    """Analyzer for structural characteristics of sentences.
    
    Analyzes sentence length distributions, identifies outliers,
    and calculates statistical metrics for character and word counts.
    
    This analyzer is language-agnostic and does not require any
    language-specific resources.
    """
    
    def __init__(self, config: Any, language_pack: Optional[Any] = None):
        """Initialize the structural analyzer.
        
        Args:
            config: Configuration object with structural thresholds
            language_pack: Optional language pack (not used by this analyzer)
        """
        super().__init__(config, language_pack)
        
        # Extract thresholds from config
        if hasattr(config, 'structural'):
            structural_config = config.structural
            self.min_words = structural_config.min_words
            self.max_words = structural_config.max_words
            self.min_chars = structural_config.min_chars
            self.max_chars = structural_config.max_chars
        else:
            # Fallback for old-style config
            self.min_words = getattr(config, 'min_words', 3)
            self.max_words = getattr(config, 'max_words', 20)
            self.min_chars = getattr(config, 'min_chars', 10)
            self.max_chars = getattr(config, 'max_chars', 200)
    
    def analyze(self, sentences: List[Sentence]) -> StructuralMetrics:
        """Analyze structural characteristics of sentences.
        
        Args:
            sentences: List of sentences to analyze
            
        Returns:
            StructuralMetrics containing all structural analysis results
        """
        if not sentences:
            return StructuralMetrics(
                total_sentences=0,
                char_distribution={},
                word_distribution={},
                too_short=[],
                too_long=[],
                length_histogram={}
            )
        
        # Compute distributions
        char_dist = self.compute_length_distribution(sentences, 'char')
        word_dist = self.compute_length_distribution(sentences, 'word')
        
        # Identify outliers
        too_short, too_long = self.identify_outliers(sentences)
        
        # Create histogram
        histogram = self._create_histogram(sentences)
        
        return StructuralMetrics(
            total_sentences=len(sentences),
            char_distribution=char_dist,
            word_distribution=word_dist,
            too_short=too_short,
            too_long=too_long,
            length_histogram=histogram
        )
    
    def compute_length_distribution(
        self, 
        sentences: List[Sentence], 
        metric: str = 'word'
    ) -> Dict[str, float]:
        """Compute statistical distribution of sentence lengths.
        
        Args:
            sentences: List of sentences to analyze
            metric: Type of length metric ('char' or 'word')
            
        Returns:
            Dictionary with statistical measures (min, max, mean, median, std)
        """
        if not sentences:
            return {}
        
        # Extract lengths based on metric type
        if metric == 'char':
            lengths = [s.char_count for s in sentences]
        else:  # word
            lengths = [s.word_count for s in sentences]
        
        # Calculate statistics
        distribution = {
            'min': float(min(lengths)),
            'max': float(max(lengths)),
            'mean': statistics.mean(lengths),
            'median': statistics.median(lengths),
        }
        
        # Add standard deviation if we have more than one sentence
        if len(lengths) > 1:
            distribution['std'] = statistics.stdev(lengths)
        else:
            distribution['std'] = 0.0
        
        return distribution
    
    def identify_outliers(
        self, 
        sentences: List[Sentence]
    ) -> tuple[List[Sentence], List[Sentence]]:
        """Identify sentences that are too short or too long.
        
        Args:
            sentences: List of sentences to analyze
            
        Returns:
            Tuple of (too_short, too_long) sentence lists
        """
        too_short = []
        too_long = []
        
        for sentence in sentences:
            if sentence.word_count < self.min_words:
                too_short.append(sentence)
            elif sentence.word_count > self.max_words:
                too_long.append(sentence)
        
        return too_short, too_long
    
    def _create_histogram(self, sentences: List[Sentence]) -> Dict[int, int]:
        """Create frequency histogram of word counts.
        
        Args:
            sentences: List of sentences to analyze
            
        Returns:
            Dictionary mapping word_count to frequency
        """
        histogram = {}
        
        for sentence in sentences:
            word_count = sentence.word_count
            histogram[word_count] = histogram.get(word_count, 0) + 1
        
        return histogram
    
    def get_requirements(self) -> List[str]:
        """Return list of required resources.
        
        The structural analyzer does not require any language-specific
        resources as it only analyzes sentence length characteristics.
        
        Returns:
            Empty list (no requirements)
        """
        return []
