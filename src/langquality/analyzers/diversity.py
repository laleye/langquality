"""Diversity analyzer for vocabulary and structural diversity metrics."""

from collections import Counter
from dataclasses import dataclass, field
from typing import Any, List, Optional, Set, Tuple
import re

from .base import Analyzer
from ..data.models import Sentence


@dataclass
class DiversityMetrics:
    """Metrics for vocabulary and structural diversity analysis.
    
    Attributes:
        ttr: Type-Token Ratio (unique words / total words)
        unique_words: Number of unique words in the dataset
        total_words: Total number of words in the dataset
        vocabulary_coverage: Proportion of reference vocabulary covered (0.0-1.0)
        bigram_distribution: Frequency distribution of bigrams
        trigram_distribution: Frequency distribution of trigrams
        repetitive_ngrams: List of n-grams that appear frequently (ngram, count)
        near_duplicates: List of sentence pairs with high similarity (s1, s2, similarity)
        sentence_starter_diversity: Diversity score for sentence starters (0.0-1.0)
    """
    ttr: float
    unique_words: int
    total_words: int
    vocabulary_coverage: float
    bigram_distribution: Counter
    trigram_distribution: Counter
    repetitive_ngrams: List[Tuple[str, int]] = field(default_factory=list)
    near_duplicates: List[Tuple[Sentence, Sentence, float]] = field(default_factory=list)
    sentence_starter_diversity: float = 0.0


class DiversityAnalyzer(Analyzer):
    """Analyzer for vocabulary and structural diversity.
    
    Analyzes vocabulary richness (TTR), n-gram distributions,
    near-duplicate detection, and sentence starter diversity.
    Supports optional reference vocabulary from language packs.
    """
    
    def __init__(self, config: Any, language_pack: Optional[Any] = None):
        """Initialize the diversity analyzer.
        
        Args:
            config: Configuration object with diversity thresholds
            language_pack: Optional language pack with reference vocabulary
        """
        super().__init__(config, language_pack)
        
        # Extract thresholds from config
        if hasattr(config, 'diversity'):
            diversity_config = config.diversity
            self.target_ttr = diversity_config.target_ttr
            self.min_unique_words = diversity_config.min_unique_words
            self.check_duplicates = diversity_config.check_duplicates
        else:
            # Fallback for old-style config
            self.target_ttr = getattr(config, 'target_ttr', 0.6)
            self.min_unique_words = getattr(config, 'min_unique_words', 100)
            self.check_duplicates = getattr(config, 'check_duplicates', True)
        
        # Load reference vocabulary from language pack or config
        self.reference_vocabulary = self._load_reference_vocabulary()
    
    def _load_reference_vocabulary(self) -> Set[str]:
        """Load reference vocabulary from language pack or config file.
        
        Returns:
            Set of reference vocabulary words, or empty set if not available
        """
        # Try to load from language pack first
        if self.language_pack and self.language_pack.has_resource('asr_vocabulary'):
            vocab_data = self.language_pack.get_resource('asr_vocabulary')
            if isinstance(vocab_data, set):
                return vocab_data
            elif isinstance(vocab_data, list):
                return {word.lower() for word in vocab_data}
        
        # Fallback to config file path (legacy support)
        reference_vocab_path = getattr(self.config, 'reference_vocabulary', None)
        if not reference_vocab_path:
            return set()
        
        try:
            with open(reference_vocab_path, 'r', encoding='utf-8') as f:
                # Read words, one per line, and normalize to lowercase
                return {line.strip().lower() for line in f if line.strip()}
        except (FileNotFoundError, IOError):
            self.logger.warning(f"Reference vocabulary file not found: {reference_vocab_path}")
            return set()
    
    def analyze(self, sentences: List[Sentence]) -> DiversityMetrics:
        """Analyze vocabulary and structural diversity of sentences.
        
        Args:
            sentences: List of sentences to analyze
            
        Returns:
            DiversityMetrics containing all diversity analysis results
        """
        if not sentences:
            return DiversityMetrics(
                ttr=0.0,
                unique_words=0,
                total_words=0,
                vocabulary_coverage=0.0,
                bigram_distribution=Counter(),
                trigram_distribution=Counter()
            )
        
        # Compute vocabulary diversity metrics
        ttr = self.compute_ttr(sentences)
        unique_words, total_words = self._extract_vocabulary_stats(sentences)
        vocab_coverage = self.compute_vocabulary_coverage(sentences)
        
        # Compute structural diversity metrics
        bigrams = self.extract_ngrams(sentences, n=2)
        trigrams = self.extract_ngrams(sentences, n=3)
        repetitive_ngrams = self._identify_repetitive_ngrams(bigrams, trigrams)
        near_duplicates = self.detect_near_duplicates(sentences)
        starter_diversity = self.analyze_sentence_starters(sentences)
        
        return DiversityMetrics(
            ttr=ttr,
            unique_words=unique_words,
            total_words=total_words,
            vocabulary_coverage=vocab_coverage,
            bigram_distribution=bigrams,
            trigram_distribution=trigrams,
            repetitive_ngrams=repetitive_ngrams,
            near_duplicates=near_duplicates,
            sentence_starter_diversity=starter_diversity
        )
    
    def compute_ttr(self, sentences: List[Sentence]) -> float:
        """Compute Type-Token Ratio (TTR) for vocabulary diversity.
        
        TTR = unique_words / total_words
        Higher TTR indicates greater vocabulary diversity.
        
        Args:
            sentences: List of sentences to analyze
            
        Returns:
            Type-Token Ratio as a float between 0.0 and 1.0
        """
        if not sentences:
            return 0.0
        
        unique_words, total_words = self._extract_vocabulary_stats(sentences)
        
        if total_words == 0:
            return 0.0
        
        return unique_words / total_words
    
    def _extract_vocabulary_stats(self, sentences: List[Sentence]) -> Tuple[int, int]:
        """Extract vocabulary statistics from sentences.
        
        Args:
            sentences: List of sentences to analyze
            
        Returns:
            Tuple of (unique_word_count, total_word_count)
        """
        all_words = []
        
        for sentence in sentences:
            # Tokenize: split on whitespace and punctuation
            words = self._tokenize(sentence.text)
            all_words.extend(words)
        
        unique_words = len(set(all_words))
        total_words = len(all_words)
        
        return unique_words, total_words
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words.
        
        Args:
            text: Text to tokenize
            
        Returns:
            List of lowercase words
        """
        # Remove punctuation and split on whitespace
        # Keep only alphabetic characters and spaces
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = text.split()
        return [w for w in words if w]  # Filter empty strings
    
    def compute_vocabulary_coverage(self, sentences: List[Sentence]) -> float:
        """Compute vocabulary coverage against reference vocabulary.
        
        Args:
            sentences: List of sentences to analyze
            
        Returns:
            Coverage ratio (0.0-1.0), or 0.0 if no reference vocabulary
        """
        if not self.reference_vocabulary:
            return 0.0
        
        # Extract all unique words from sentences
        dataset_words = set()
        for sentence in sentences:
            words = self._tokenize(sentence.text)
            dataset_words.update(words)
        
        if not dataset_words:
            return 0.0
        
        # Calculate how many reference words are covered
        covered_words = dataset_words.intersection(self.reference_vocabulary)
        coverage = len(covered_words) / len(self.reference_vocabulary)
        
        return coverage
    
    def extract_ngrams(self, sentences: List[Sentence], n: int) -> Counter:
        """Extract n-grams from sentences and compute frequency distribution.
        
        Args:
            sentences: List of sentences to analyze
            n: Size of n-grams (2 for bigrams, 3 for trigrams)
            
        Returns:
            Counter with n-gram frequencies
        """
        ngrams = []
        
        for sentence in sentences:
            words = self._tokenize(sentence.text)
            
            # Extract n-grams from this sentence
            for i in range(len(words) - n + 1):
                ngram = tuple(words[i:i+n])
                ngrams.append(ngram)
        
        return Counter(ngrams)
    
    def _identify_repetitive_ngrams(
        self, 
        bigrams: Counter, 
        trigrams: Counter,
        threshold: int = 5
    ) -> List[Tuple[str, int]]:
        """Identify n-grams that appear frequently.
        
        Args:
            bigrams: Bigram frequency distribution
            trigrams: Trigram frequency distribution
            threshold: Minimum frequency to be considered repetitive
            
        Returns:
            List of (ngram_string, count) tuples for repetitive n-grams
        """
        repetitive = []
        
        # Check bigrams
        for ngram, count in bigrams.items():
            if count >= threshold:
                ngram_str = ' '.join(ngram)
                repetitive.append((ngram_str, count))
        
        # Check trigrams
        for ngram, count in trigrams.items():
            if count >= threshold:
                ngram_str = ' '.join(ngram)
                repetitive.append((ngram_str, count))
        
        # Sort by frequency (descending)
        repetitive.sort(key=lambda x: x[1], reverse=True)
        
        return repetitive
    
    def detect_near_duplicates(
        self, 
        sentences: List[Sentence],
        similarity_threshold: float = 0.8
    ) -> List[Tuple[Sentence, Sentence, float]]:
        """Detect sentence pairs with high similarity.
        
        Uses Jaccard similarity on word sets to identify near-duplicates.
        
        Args:
            sentences: List of sentences to analyze
            similarity_threshold: Minimum similarity to be considered near-duplicate
            
        Returns:
            List of (sentence1, sentence2, similarity_score) tuples
        """
        near_duplicates = []
        
        # Precompute word sets for all sentences
        sentence_word_sets = []
        for sentence in sentences:
            words = set(self._tokenize(sentence.text))
            sentence_word_sets.append((sentence, words))
        
        # Compare all pairs
        for i in range(len(sentence_word_sets)):
            for j in range(i + 1, len(sentence_word_sets)):
                sent1, words1 = sentence_word_sets[i]
                sent2, words2 = sentence_word_sets[j]
                
                # Calculate Jaccard similarity
                similarity = self._jaccard_similarity(words1, words2)
                
                if similarity >= similarity_threshold:
                    near_duplicates.append((sent1, sent2, similarity))
        
        # Sort by similarity (descending)
        near_duplicates.sort(key=lambda x: x[2], reverse=True)
        
        return near_duplicates
    
    def _jaccard_similarity(self, set1: Set[str], set2: Set[str]) -> float:
        """Calculate Jaccard similarity between two sets.
        
        Jaccard similarity = |intersection| / |union|
        
        Args:
            set1: First set of words
            set2: Second set of words
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        if not set1 and not set2:
            return 1.0
        
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def analyze_sentence_starters(self, sentences: List[Sentence]) -> float:
        """Analyze diversity of sentence starters.
        
        Measures how diverse the first words/phrases of sentences are.
        Higher diversity indicates more varied sentence structures.
        
        Args:
            sentences: List of sentences to analyze
            
        Returns:
            Diversity score between 0.0 and 1.0
        """
        if not sentences:
            return 0.0
        
        # Extract first word from each sentence
        starters = []
        for sentence in sentences:
            words = self._tokenize(sentence.text)
            if words:
                starters.append(words[0])
        
        if not starters:
            return 0.0
        
        # Calculate diversity as ratio of unique starters to total sentences
        unique_starters = len(set(starters))
        total_starters = len(starters)
        
        diversity = unique_starters / total_starters
        
        return diversity
    
    def get_requirements(self) -> List[str]:
        """Return list of required resources.
        
        The diversity analyzer can optionally use a reference vocabulary
        (ASR vocabulary) for coverage analysis, but can function without it.
        
        Returns:
            Empty list (no required resources)
        """
        # Reference vocabulary is optional
        return []
