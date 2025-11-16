"""Test analyzer that requires resources."""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from src.langquality.analyzers.base import Analyzer
from src.langquality.data.models import Sentence
from src.langquality.language_packs.models import LanguagePack


@dataclass
class ResourceMetrics:
    """Metrics from resource-dependent analyzer."""
    total_sentences: int = 0
    lexicon_matches: int = 0
    has_lexicon: bool = False


class TestResourceAnalyzer(Analyzer):
    """An analyzer that requires lexicon resource for testing."""
    
    def __init__(self, config=None, language_pack: Optional[LanguagePack] = None):
        """Initialize the resource analyzer.
        
        Args:
            config: Configuration object (optional)
            language_pack: Language pack (optional)
        """
        super().__init__(config, language_pack)
        self._name = "test_resource"
        self._version = "1.0.0"
    
    def analyze(self, sentences: List[Sentence]) -> ResourceMetrics:
        """Perform analysis requiring lexicon resource.
        
        Args:
            sentences: List of sentences to analyze
            
        Returns:
            ResourceMetrics with analysis results
        """
        metrics = ResourceMetrics()
        metrics.total_sentences = len(sentences)
        
        if self.language_pack and self.language_pack.has_resource("lexicon"):
            metrics.has_lexicon = True
            lexicon = self.language_pack.get_resource("lexicon", [])
            lexicon_set = set(word.lower() for word in lexicon)
            
            # Count matches with lexicon
            for sentence in sentences:
                words = sentence.text.lower().split()
                for word in words:
                    if word in lexicon_set:
                        metrics.lexicon_matches += 1
        
        return metrics
    
    def get_requirements(self) -> List[str]:
        """Return list of required resources.
        
        Returns:
            List containing 'lexicon'
        """
        return ["lexicon"]
    
    def can_run(self) -> Tuple[bool, Optional[str]]:
        """Check if analyzer can run.
        
        Returns:
            Tuple of (can_run, reason)
        """
        if not self.language_pack:
            return False, "No language pack provided"
        
        if not self.language_pack.has_resource("lexicon"):
            return False, "Missing required resource: lexicon"
        
        return True, None
    
    @property
    def name(self) -> str:
        """Return analyzer name."""
        return self._name
    
    @property
    def version(self) -> str:
        """Return analyzer version."""
        return self._version
