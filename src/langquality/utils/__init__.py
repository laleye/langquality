"""Utility modules."""

from .exceptions import (
    LangQualityError,
    DataLoadError,
    ValidationError,
    AnalysisError,
    ConfigurationError,
)

# Backward compatibility alias
FongbeQualityError = LangQualityError

__all__ = [
    "LangQualityError",
    "FongbeQualityError",  # Deprecated alias
    "DataLoadError",
    "ValidationError",
    "AnalysisError",
    "ConfigurationError",
]
