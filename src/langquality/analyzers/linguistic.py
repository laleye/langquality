"""Linguistic analyzer for readability and complexity metrics."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import os
import re
import textstat

from .base import Analyzer
from ..data.models import Sentence


@dataclass
class LinguisticMetrics:
    """Metrics for linguistic analysis of sentences.
    
    Attributes:
        avg_readability_score: Average Flesch-Kincaid readability score
        readability_distribution: List of readability scores per sentence
        avg_lexical_complexity: Average lexical complexity score
        jargon_detected: Dictionary mapping sentence indices to detected jargon terms
        complex_syntax_count: Number of sentences with complex syntax
        complex_sentences: List of sentences with complex syntax
    """
    avg_readability_score: float
    readability_distribution: List[float]
    avg_lexical_complexity: float
    jargon_detected: Dict[str, List[str]]
    complex_syntax_count: int
    complex_sentences: List[Sentence] = field(default_factory=list)


class LinguisticAnalyzer(Analyzer):
    """Analyzer for linguistic complexity and readability.
    
    Analyzes readability scores, lexical complexity, jargon detection,
    and syntactic complexity using NLP tools. Supports multi-language
    analysis through language packs.
    """
    
    def __init__(self, config: Any, language_pack: Optional[Any] = None):
        """Initialize the linguistic analyzer.
        
        Args:
            config: Configuration object with linguistic thresholds
            language_pack: Optional language pack with lexicon and other resources
        """
        super().__init__(config, language_pack)
        
        # Extract thresholds from config
        if hasattr(config, 'linguistic'):
            linguistic_config = config.linguistic
            self.max_readability_score = linguistic_config.max_readability_score
            self.enable_pos_tagging = linguistic_config.enable_pos_tagging
            self.enable_dependency_parsing = linguistic_config.enable_dependency_parsing
        else:
            # Fallback for old-style config
            self.max_readability_score = getattr(config, 'max_readability_score', 60.0)
            self.enable_pos_tagging = getattr(config, 'enable_pos_tagging', True)
            self.enable_dependency_parsing = getattr(config, 'enable_dependency_parsing', False)
        
        # Legacy support
        self.min_readability_score = getattr(config, 'min_readability_score', 0.0)
        self.jargon_terms = set(term.lower() for term in getattr(config, 'jargon_terms', []))
        
        # Load frequency lexicon from language pack or fallback
        self.frequency_lexicon = self._load_frequency_lexicon()
        
        # Load spaCy model (lazy loading)
        self._nlp = None
    
    @property
    def nlp(self):
        """Lazy load spaCy model based on language pack configuration."""
        if self._nlp is None:
            try:
                import spacy
                
                # Get model name from language pack or use default
                model_name = "fr_core_news_md"  # Default
                
                if self.language_pack and hasattr(self.language_pack.config, 'tokenization'):
                    tokenization_config = self.language_pack.config.tokenization
                    if tokenization_config.method == 'spacy' and tokenization_config.model:
                        model_name = tokenization_config.model
                
                self._nlp = spacy.load(model_name)
            except (OSError, ImportError):
                # Model not installed or spaCy not available
                # This allows the analyzer to work without spaCy for basic features
                self.logger.warning(f"spaCy model not available, using fallback methods")
                self._nlp = None
        return self._nlp
    
    def _load_frequency_lexicon(self) -> Dict[str, int]:
        """Load word frequency lexicon from language pack or fallback.
        
        Returns:
            Dictionary mapping words to frequency ranks (lower = more common)
        """
        lexicon = {}
        
        # Try to load from language pack first
        if self.language_pack and self.language_pack.has_resource('lexicon'):
            lexicon_data = self.language_pack.get_resource('lexicon')
            if isinstance(lexicon_data, dict):
                return lexicon_data
            elif isinstance(lexicon_data, list):
                # Convert list to dict with ranks
                return {word.lower(): idx + 1 for idx, word in enumerate(lexicon_data)}
        
        # Fallback: load from default resources directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        resources_dir = os.path.join(os.path.dirname(current_dir), 'resources')
        lexicon_path = os.path.join(resources_dir, 'french_frequency_lexicon.txt')
        
        try:
            with open(lexicon_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    
                    parts = line.split()
                    if len(parts) >= 2:
                        word = parts[0].lower()
                        try:
                            rank = int(parts[1])
                            lexicon[word] = rank
                        except ValueError:
                            continue
        except FileNotFoundError:
            self.logger.warning("Frequency lexicon not found, lexical complexity analysis will be limited")
        
        return lexicon
    
    def analyze(self, sentences: List[Sentence]) -> LinguisticMetrics:
        """Analyze linguistic characteristics of sentences.
        
        Args:
            sentences: List of sentences to analyze
            
        Returns:
            LinguisticMetrics containing all linguistic analysis results
        """
        if not sentences:
            return LinguisticMetrics(
                avg_readability_score=0.0,
                readability_distribution=[],
                avg_lexical_complexity=0.0,
                jargon_detected={},
                complex_syntax_count=0,
                complex_sentences=[]
            )
        
        readability_scores = []
        lexical_complexity_scores = []
        jargon_detected = {}
        complex_sentences = []
        
        for idx, sentence in enumerate(sentences):
            # Compute readability score
            readability = self.compute_readability_score(sentence)
            readability_scores.append(readability)
            
            # Compute lexical complexity
            complexity = self.compute_lexical_complexity(sentence)
            lexical_complexity_scores.append(complexity)
            
            # Detect jargon
            jargon = self.detect_jargon(sentence)
            if jargon:
                jargon_detected[f"{sentence.source_file}:{sentence.line_number}"] = jargon
            
            # Detect complex syntax
            if self.detect_complex_syntax(sentence):
                complex_sentences.append(sentence)
        
        # Calculate averages
        avg_readability = sum(readability_scores) / len(readability_scores) if readability_scores else 0.0
        avg_complexity = sum(lexical_complexity_scores) / len(lexical_complexity_scores) if lexical_complexity_scores else 0.0
        
        return LinguisticMetrics(
            avg_readability_score=avg_readability,
            readability_distribution=readability_scores,
            avg_lexical_complexity=avg_complexity,
            jargon_detected=jargon_detected,
            complex_syntax_count=len(complex_sentences),
            complex_sentences=complex_sentences
        )

    def compute_readability_score(self, sentence: Sentence) -> float:
        """Compute Flesch-Kincaid readability score for a sentence.
        
        Uses the Flesch Reading Ease score adapted for French.
        Higher scores indicate easier readability.
        
        Args:
            sentence: Sentence to analyze
            
        Returns:
            Readability score (0-100, higher = easier to read)
        """
        try:
            # Use textstat's Flesch Reading Ease for French
            # Note: textstat.flesch_reading_ease works for French text
            score = textstat.flesch_reading_ease(sentence.text)
            return max(0.0, min(100.0, score))  # Clamp to 0-100
        except Exception:
            # If calculation fails, return neutral score
            return 50.0
    
    def compute_lexical_complexity(self, sentence: Sentence) -> float:
        """Compute lexical complexity based on word frequency.
        
        Calculates complexity by checking how many words are rare
        (not in the common frequency lexicon). Higher scores indicate
        more complex/rare vocabulary.
        
        Args:
            sentence: Sentence to analyze
            
        Returns:
            Complexity score (0.0-1.0, higher = more complex)
        """
        if not self.frequency_lexicon:
            return 0.0
        
        # Tokenize into words (simple approach)
        words = re.findall(r'\b\w+\b', sentence.text.lower())
        
        if not words:
            return 0.0
        
        # Count rare words (not in top frequency list)
        rare_word_count = 0
        total_complexity = 0.0
        
        for word in words:
            if word in self.frequency_lexicon:
                # Word is in lexicon - use inverse of rank as complexity
                # Higher rank = less common = more complex
                rank = self.frequency_lexicon[word]
                # Normalize: words with rank > 100 are considered rare
                complexity = min(1.0, rank / 100.0)
                total_complexity += complexity
            else:
                # Word not in lexicon - considered rare/complex
                rare_word_count += 1
                total_complexity += 1.0
        
        # Return average complexity
        return total_complexity / len(words) if words else 0.0
    
    def detect_jargon(self, sentence: Sentence) -> List[str]:
        """Detect jargon and technical terms in a sentence.
        
        Checks for configured jargon terms and identifies potential
        technical vocabulary.
        
        Args:
            sentence: Sentence to analyze
            
        Returns:
            List of detected jargon terms
        """
        detected = []
        
        # Tokenize sentence
        words = re.findall(r'\b\w+\b', sentence.text.lower())
        
        # Check against configured jargon terms
        for word in words:
            if word in self.jargon_terms:
                detected.append(word)
        
        # Additional heuristic: very long words (>12 chars) might be technical
        for word in words:
            if len(word) > 12 and word not in self.frequency_lexicon:
                if word not in detected:
                    detected.append(word)
        
        return detected
    
    def detect_complex_syntax(self, sentence: Sentence) -> bool:
        """Detect complex syntactic structures using spaCy.
        
        Identifies sentences with:
        - Multiple subordinate clauses
        - Passive voice constructions
        - Deep syntactic trees
        
        Args:
            sentence: Sentence to analyze
            
        Returns:
            True if sentence has complex syntax, False otherwise
        """
        # If spaCy is not available, use simple heuristics
        if self.nlp is None:
            return self._detect_complex_syntax_simple(sentence)
        
        try:
            doc = self.nlp(sentence.text)
            
            # Count subordinate clauses (marked by subordinating conjunctions)
            subordinate_count = 0
            passive_voice = False
            max_depth = 0
            
            for token in doc:
                # Check for subordinating conjunctions
                if token.dep_ in ['mark', 'advcl', 'acl', 'ccomp', 'xcomp']:
                    subordinate_count += 1
                
                # Check for passive voice (auxiliary + past participle)
                if token.dep_ == 'auxpass':
                    passive_voice = True
                
                # Calculate tree depth
                depth = self._get_token_depth(token)
                max_depth = max(max_depth, depth)
            
            # Consider complex if:
            # - More than 2 subordinate clauses
            # - Passive voice with long sentence
            # - Deep syntactic tree (depth > 5)
            is_complex = (
                subordinate_count > 2 or
                (passive_voice and sentence.word_count > 15) or
                max_depth > 5
            )
            
            return is_complex
            
        except Exception:
            # Fall back to simple heuristics if spaCy fails
            return self._detect_complex_syntax_simple(sentence)
    
    def _detect_complex_syntax_simple(self, sentence: Sentence) -> bool:
        """Simple heuristic-based complex syntax detection.
        
        Used as fallback when spaCy is not available.
        
        Args:
            sentence: Sentence to analyze
            
        Returns:
            True if sentence appears to have complex syntax
        """
        text = sentence.text.lower()
        
        # Count subordinating conjunctions and relative pronouns
        complex_markers = [
            'que', 'qui', 'dont', 'où', 'lequel', 'laquelle',
            'parce que', 'bien que', 'quoique', 'puisque',
            'lorsque', 'tandis que', 'afin que', 'pour que'
        ]
        
        marker_count = sum(1 for marker in complex_markers if marker in text)
        
        # Count commas (indicator of clause complexity)
        comma_count = text.count(',')
        
        # Consider complex if multiple markers or many commas with long sentence
        return marker_count > 2 or (comma_count > 2 and sentence.word_count > 15)
    
    def _get_token_depth(self, token) -> int:
        """Calculate the depth of a token in the dependency tree.
        
        Args:
            token: spaCy token
            
        Returns:
            Depth in the tree (root = 0)
        """
        depth = 0
        current = token
        
        while current.head != current:
            depth += 1
            current = current.head
            # Prevent infinite loops
            if depth > 20:
                break
        
        return depth
    
    def get_requirements(self) -> List[str]:
        """Return list of required resources.
        
        The linguistic analyzer can optionally use a frequency lexicon
        for lexical complexity analysis, but can function without it.
        
        Returns:
            List of optional resource names
        """
        # Lexicon is optional - analyzer can work without it
        return []
