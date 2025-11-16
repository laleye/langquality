"""Custom exceptions for the LangQuality analysis toolkit."""


class LangQualityError(Exception):
    """Base exception for all LangQuality errors."""
    pass


class DataLoadError(LangQualityError):
    """Exception raised when data loading fails."""
    pass


class ValidationError(LangQualityError):
    """Exception raised when data validation fails."""
    pass


class AnalysisError(LangQualityError):
    """Exception raised when analysis execution fails."""
    pass


class ConfigurationError(LangQualityError):
    """Exception raised when configuration is invalid or cannot be loaded."""
    pass
