"""
LangQuality - Language Quality Toolkit for Low-Resource Languages

A modular, extensible toolkit for analyzing the quality of text data
for low-resource languages. Supports multiple languages through
configurable language packs.
"""

__version__ = "1.0.0"
__author__ = "LangQuality Community"

from .data.models import Sentence, ValidationResult
from .config.models import AnalysisConfig, PipelineConfig
from .pipeline.controller import PipelineController

__all__ = [
    "Sentence",
    "ValidationResult",
    "AnalysisConfig",
    "PipelineConfig",
    "PipelineController",
]
