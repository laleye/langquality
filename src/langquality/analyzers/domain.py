"""Domain analyzer for thematic distribution metrics."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .base import Analyzer
from ..data.models import Sentence


@dataclass
class DomainMetrics:
    """Metrics for domain distribution analysis.
    
    Attributes:
        domain_counts: Number of sentences per domain
        domain_percentages: Percentage of each domain in the dataset
        underrepresented: List of domains with less than 10% representation
        overrepresented: List of domains with more than 30% representation
        total_domains: Total number of unique domains
    """
    domain_counts: Dict[str, int] = field(default_factory=dict)
    domain_percentages: Dict[str, float] = field(default_factory=dict)
    underrepresented: List[str] = field(default_factory=list)
    overrepresented: List[str] = field(default_factory=list)
    total_domains: int = 0


class DomainAnalyzer(Analyzer):
    """Analyzer for domain distribution and balance.
    
    Analyzes the distribution of sentences across different thematic domains,
    identifies underrepresented and overrepresented domains to ensure
    balanced dataset coverage. This analyzer is language-agnostic.
    """
    
    def __init__(self, config: Any, language_pack: Optional[Any] = None):
        """Initialize the domain analyzer.
        
        Args:
            config: Configuration object with domain thresholds
            language_pack: Optional language pack (not used by this analyzer)
        """
        super().__init__(config, language_pack)
        
        # Extract thresholds from config
        if hasattr(config, 'domain'):
            domain_config = config.domain
            self.min_domain_representation = domain_config.min_representation
            self.max_domain_representation = domain_config.max_representation
            self.balance_threshold = domain_config.balance_threshold
        else:
            # Fallback for old-style config
            self.min_domain_representation = getattr(config, 'min_domain_representation', 0.10)
            self.max_domain_representation = getattr(config, 'max_domain_representation', 0.30)
            self.balance_threshold = getattr(config, 'balance_threshold', 0.15)
    
    def analyze(self, sentences: List[Sentence]) -> DomainMetrics:
        """Analyze domain distribution of sentences.
        
        Args:
            sentences: List of sentences to analyze
            
        Returns:
            DomainMetrics containing all domain analysis results
        """
        if not sentences:
            return DomainMetrics(
                domain_counts={},
                domain_percentages={},
                underrepresented=[],
                overrepresented=[],
                total_domains=0
            )
        
        # Compute domain distribution
        domain_counts = self.compute_domain_distribution(sentences)
        
        # Calculate percentages
        total_sentences = len(sentences)
        domain_percentages = {
            domain: (count / total_sentences)
            for domain, count in domain_counts.items()
        }
        
        # Identify imbalanced domains
        underrepresented = self.identify_underrepresented_domains(domain_percentages)
        overrepresented = self.identify_overrepresented_domains(domain_percentages)
        
        return DomainMetrics(
            domain_counts=domain_counts,
            domain_percentages=domain_percentages,
            underrepresented=underrepresented,
            overrepresented=overrepresented,
            total_domains=len(domain_counts)
        )
    
    def compute_domain_distribution(
        self, 
        sentences: List[Sentence]
    ) -> Dict[str, int]:
        """Compute the distribution of sentences across domains.
        
        Args:
            sentences: List of sentences to analyze
            
        Returns:
            Dictionary mapping domain names to sentence counts
        """
        domain_counts = {}
        
        for sentence in sentences:
            domain = sentence.domain
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        return domain_counts
    
    def identify_underrepresented_domains(
        self, 
        distribution: Dict[str, float]
    ) -> List[str]:
        """Identify domains with less than minimum representation threshold.
        
        Args:
            distribution: Dictionary mapping domains to their percentages
            
        Returns:
            List of underrepresented domain names
        """
        underrepresented = []
        
        for domain, percentage in distribution.items():
            if percentage < self.min_domain_representation:
                underrepresented.append(domain)
        
        return sorted(underrepresented)
    
    def identify_overrepresented_domains(
        self, 
        distribution: Dict[str, float]
    ) -> List[str]:
        """Identify domains with more than maximum representation threshold.
        
        Args:
            distribution: Dictionary mapping domains to their percentages
            
        Returns:
            List of overrepresented domain names
        """
        overrepresented = []
        
        for domain, percentage in distribution.items():
            if percentage > self.max_domain_representation:
                overrepresented.append(domain)
        
        return sorted(overrepresented)
    
    def get_requirements(self) -> List[str]:
        """Return list of required resources.
        
        The domain analyzer does not require any language-specific
        resources as it only analyzes domain distribution.
        
        Returns:
            Empty list (no requirements)
        """
        return []

