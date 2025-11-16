"""Base analyzer class for all quality analyzers.

This module defines the abstract base class that all analyzers must inherit from.
Each analyzer implements specific quality metrics for the dataset.
"""

from abc import ABC, abstractmethod
import logging
from typing import Any, List, Optional, Tuple

from ..data.models import Sentence


class Analyzer(ABC):
    """Abstract base class for all quality analyzers.
    
    All analyzers must inherit from this class and implement the analyze method.
    Each analyzer is responsible for computing specific quality metrics on a
    collection of sentences.
    
    The analyze method should return a metrics dataclass specific to that analyzer
    (e.g., StructuralMetrics, LinguisticMetrics, etc.).
    
    Attributes:
        config: Configuration object for the analyzer
        language_pack: Optional language pack with language-specific resources
        logger: Logger instance for the analyzer
    """
    
    def __init__(self, config: Any, language_pack: Optional[Any] = None):
        """Initialize the analyzer.
        
        Args:
            config: Configuration object containing analyzer settings
            language_pack: Optional LanguagePack with language-specific resources
        """
        self.config = config
        self.language_pack = language_pack
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def analyze(self, sentences: List[Sentence]) -> Any:
        """Analyze the given sentences and return metrics.
        
        This method must be implemented by all subclasses to perform
        specific quality analysis on the provided sentences.
        
        Args:
            sentences: List of Sentence objects to analyze
            
        Returns:
            Metrics object specific to the analyzer (e.g., StructuralMetrics,
            LinguisticMetrics, DiversityMetrics, etc.)
            
        Raises:
            AnalysisError: If analysis fails due to invalid data or processing errors
        """
        pass
    
    @abstractmethod
    def get_requirements(self) -> List[str]:
        """Return list of required resources.
        
        This method should return a list of resource names that the analyzer
        requires from the language pack. If the analyzer doesn't require any
        language-specific resources, return an empty list.
        
        Returns:
            List of required resource names (e.g., ['lexicon', 'gender_terms'])
        """
        pass
    
    def can_run(self) -> Tuple[bool, Optional[str]]:
        """Check if analyzer can run with available resources.
        
        This method checks whether all required resources are available in the
        language pack. If no language pack is provided or no resources are
        required, the analyzer can run.
        
        Returns:
            Tuple of (can_run, reason) where:
                - can_run: True if analyzer can run, False otherwise
                - reason: Optional string explaining why analyzer cannot run
        """
        requirements = self.get_requirements()
        
        # If no requirements, analyzer can always run
        if not requirements:
            return True, None
        
        # If no language pack but requirements exist, cannot run
        if not self.language_pack:
            return False, "No language pack provided but resources are required"
        
        # Check each requirement
        for req in requirements:
            if not self.language_pack.has_resource(req):
                return False, f"Missing required resource: {req}"
        
        return True, None
    
    @property
    def name(self) -> str:
        """Return analyzer name.
        
        Returns:
            Name of the analyzer (class name without 'Analyzer' suffix)
        """
        class_name = self.__class__.__name__
        if class_name.endswith('Analyzer'):
            return class_name[:-8]  # Remove 'Analyzer' suffix
        return class_name
    
    @property
    def version(self) -> str:
        """Return analyzer version.
        
        Subclasses can override this to provide specific version information.
        
        Returns:
            Version string (default: '1.0.0')
        """
        return "1.0.0"
