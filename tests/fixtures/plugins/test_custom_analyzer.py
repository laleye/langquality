"""Test custom analyzer plugin for testing the plugin system."""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from src.langquality.analyzers.base import Analyzer
from src.langquality.data.models import Sentence
from src.langquality.language_packs.models import LanguagePack


@dataclass
class CustomMetrics:
    """Metrics from custom analyzer."""
    total_sentences: int = 0
    custom_score: float = 0.0
    custom_flags: List[str] = field(default_factory=list)


class TestCustomAnalyzer(Analyzer):
    """A simple custom analyzer for testing the plugin system.
    
    This analyzer counts sentences and assigns a custom score.
    """
    
    def __init__(self, config=None, language_pack: Optional[LanguagePack] = None):
        """Initialize the custom analyzer.
        
        Args:
            config: Configuration object (optional)
            language_pack: Language pack (optional)
        """
        super().__init__(config, language_pack)
        self._name = "test_custom"
        self._version = "1.0.0"
    
    def analyze(self, sentences: List[Sentence]) -> CustomMetrics:
        """Perform custom analysis on sentences.
        
        Args:
            sentences: List of sentences to analyze
            
        Returns:
            CustomMetrics with analysis results
        """
        metrics = CustomMetrics()
        metrics.total_sentences = len(sentences)
        
        # Simple custom logic: score based on average word count
        if sentences:
            total_words = sum(s.word_count for s in sentences)
            avg_words = total_words / len(sentences)
            metrics.custom_score = min(avg_words / 10.0, 1.0)
        
        # Add custom flags
        for sentence in sentences:
            if sentence.word_count > 15:
                metrics.custom_flags.append(f"Long sentence: {sentence.text[:50]}...")
        
        return metrics
    
    def get_requirements(self) -> List[str]:
        """Return list of required resources.
        
        Returns:
            Empty list (no requirements)
        """
        return []
    
    def can_run(self) -> Tuple[bool, Optional[str]]:
        """Check if analyzer can run.
        
        Returns:
            Tuple of (True, None) since this analyzer has no requirements
        """
        return True, None
    
    @property
    def name(self) -> str:
        """Return analyzer name."""
        return self._name
    
    @property
    def version(self) -> str:
        """Return analyzer version."""
        return self._version
