"""Analysis results data model."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ..analyzers.structural import StructuralMetrics
from ..analyzers.linguistic import LinguisticMetrics
from ..analyzers.diversity import DiversityMetrics
from ..analyzers.domain import DomainMetrics
from ..analyzers.gender_bias import GenderBiasMetrics
from ..config.models import PipelineConfig


@dataclass
class AnalysisResults:
    """Aggregates all analysis results from the pipeline.
    
    Attributes:
        structural: Structural analysis metrics (sentence lengths, distributions)
        linguistic: Linguistic analysis metrics (readability, complexity)
        diversity: Diversity analysis metrics (TTR, n-grams, duplicates)
        domain: Domain distribution metrics
        gender_bias: Gender bias detection metrics
        timestamp: When the analysis was performed
        config_used: Configuration used for this analysis
    """
    structural: Optional[StructuralMetrics]
    linguistic: Optional[LinguisticMetrics]
    diversity: Optional[DiversityMetrics]
    domain: Optional[DomainMetrics]
    gender_bias: Optional[GenderBiasMetrics]
    timestamp: datetime
    config_used: PipelineConfig
