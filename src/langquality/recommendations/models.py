"""Recommendation data models."""

from dataclasses import dataclass, field
from typing import List, Any


@dataclass
class Recommendation:
    """Represents a recommendation for improving data quality."""
    
    category: str
    severity: str
    title: str
    description: str
    affected_items: List[Any] = field(default_factory=list)
    suggested_actions: List[str] = field(default_factory=list)
    priority: int = 1
