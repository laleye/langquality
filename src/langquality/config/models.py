"""Configuration models for the analysis pipeline."""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class AnalysisConfig:
    """Configuration for analysis parameters and thresholds.
    
    Attributes:
        min_words: Minimum acceptable word count per sentence
        max_words: Maximum acceptable word count per sentence
        min_readability_score: Minimum Flesch-Kincaid readability score
        max_readability_score: Maximum Flesch-Kincaid readability score
        target_ttr: Target Type-Token Ratio for vocabulary diversity
        min_domain_representation: Minimum acceptable domain representation (0.0-1.0)
        max_domain_representation: Maximum acceptable domain representation (0.0-1.0)
        target_gender_ratio: Acceptable range for feminine/masculine ratio (min, max)
        jargon_terms: List of technical terms to flag as jargon
        reference_vocabulary: Path to reference vocabulary file (optional)
    """
    min_words: int = 3
    max_words: int = 20
    min_readability_score: float = 0.0
    max_readability_score: float = 60.0
    target_ttr: float = 0.6
    min_domain_representation: float = 0.10
    max_domain_representation: float = 0.30
    target_gender_ratio: Tuple[float, float] = (0.4, 0.6)
    jargon_terms: List[str] = field(default_factory=list)
    reference_vocabulary: Optional[str] = None


@dataclass
class PipelineConfig:
    """Configuration for the entire pipeline execution.
    
    Attributes:
        analysis: Analysis-specific configuration
        input_directory: Path to directory containing input CSV files
        output_directory: Path to directory for output files
        enable_analyzers: List of analyzer names to enable (default: ["all"])
        language: Language code for text analysis (default: "fr")
    """
    analysis: AnalysisConfig
    input_directory: str
    output_directory: str
    enable_analyzers: List[str] = field(default_factory=lambda: ["all"])
    language: str = "fr"
