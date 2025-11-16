"""Data models for the LangQuality analysis toolkit."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Sentence:
    """Represents a sentence with its metadata.
    
    Attributes:
        text: The actual sentence text in French
        domain: Thematic category (health, education, commerce, etc.)
        source_file: Name of the CSV file this sentence came from
        line_number: Line number in the source file
        char_count: Number of characters in the sentence
        word_count: Number of words in the sentence
        metadata: Additional metadata as key-value pairs
    """
    text: str
    domain: str
    source_file: str
    line_number: int
    char_count: int
    word_count: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Result of data validation.
    
    Attributes:
        is_valid: Whether the data passed validation
        errors: List of error messages if validation failed
        warnings: List of warning messages
    """
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
