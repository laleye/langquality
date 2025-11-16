"""Data models for Language Pack system."""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class TokenizationConfig:
    """Configuration for text tokenization.
    
    Attributes:
        method: Tokenization method ('spacy', 'nltk', 'whitespace', 'custom')
        model: Model name for spacy/nltk (e.g., 'fr_core_news_md')
        custom_rules: List of custom tokenization rules
    """
    method: str = "whitespace"
    model: Optional[str] = None
    custom_rules: List[str] = field(default_factory=list)


@dataclass
class StructuralThresholds:
    """Thresholds for structural analysis.
    
    Attributes:
        min_words: Minimum acceptable word count per sentence
        max_words: Maximum acceptable word count per sentence
        min_chars: Minimum acceptable character count per sentence
        max_chars: Maximum acceptable character count per sentence
    """
    min_words: int = 3
    max_words: int = 20
    min_chars: int = 10
    max_chars: int = 200


@dataclass
class LinguisticThresholds:
    """Thresholds for linguistic analysis.
    
    Attributes:
        max_readability_score: Maximum Flesch-Kincaid readability score
        enable_pos_tagging: Whether to enable part-of-speech tagging
        enable_dependency_parsing: Whether to enable dependency parsing
    """
    max_readability_score: float = 60.0
    enable_pos_tagging: bool = True
    enable_dependency_parsing: bool = False


@dataclass
class DiversityThresholds:
    """Thresholds for diversity analysis.
    
    Attributes:
        target_ttr: Target Type-Token Ratio for vocabulary diversity
        min_unique_words: Minimum number of unique words in dataset
        check_duplicates: Whether to check for duplicate sentences
    """
    target_ttr: float = 0.6
    min_unique_words: int = 100
    check_duplicates: bool = True


@dataclass
class DomainThresholds:
    """Thresholds for domain balance analysis.
    
    Attributes:
        min_representation: Minimum acceptable domain representation (0.0-1.0)
        max_representation: Maximum acceptable domain representation (0.0-1.0)
        balance_threshold: Threshold for considering domains balanced
    """
    min_representation: float = 0.10
    max_representation: float = 0.30
    balance_threshold: float = 0.15


@dataclass
class GenderThresholds:
    """Thresholds for gender bias analysis.
    
    Attributes:
        target_ratio: Acceptable range for feminine/masculine ratio (min, max)
        check_stereotypes: Whether to check for gender stereotypes
    """
    target_ratio: Tuple[float, float] = (0.4, 0.6)
    check_stereotypes: bool = True


@dataclass
class ThresholdConfig:
    """Complete threshold configuration for all analyzers.
    
    Attributes:
        structural: Structural analysis thresholds
        linguistic: Linguistic analysis thresholds
        diversity: Diversity analysis thresholds
        domain: Domain balance thresholds
        gender: Gender bias thresholds
    """
    structural: Optional[StructuralThresholds] = None
    linguistic: Optional[LinguisticThresholds] = None
    diversity: Optional[DiversityThresholds] = None
    domain: Optional[DomainThresholds] = None
    gender: Optional[GenderThresholds] = None
    
    def __post_init__(self):
        """Initialize default thresholds if not provided."""
        if self.structural is None:
            self.structural = StructuralThresholds()
        if self.linguistic is None:
            self.linguistic = LinguisticThresholds()
        if self.diversity is None:
            self.diversity = DiversityThresholds()
        if self.domain is None:
            self.domain = DomainThresholds()
        if self.gender is None:
            self.gender = GenderThresholds()


@dataclass
class AnalyzerConfig:
    """Configuration for enabled/disabled analyzers.
    
    Attributes:
        enabled: List of enabled analyzer names
        disabled: List of disabled analyzer names
    """
    enabled: List[str] = field(default_factory=lambda: [
        "structural", "linguistic", "diversity", "domain"
    ])
    disabled: List[str] = field(default_factory=list)


@dataclass
class ResourceConfig:
    """Configuration for language-specific resources.
    
    Attributes:
        lexicon: Path to frequency lexicon file
        stopwords: Path to stopwords file
        gender_terms: Path to gender terms JSON file
        professions: Path to gendered professions JSON file
        stereotypes: Path to gender stereotypes JSON file
        asr_vocabulary: Path to ASR reference vocabulary file
        custom: List of paths to custom resource files
    """
    lexicon: Optional[str] = None
    stopwords: Optional[str] = None
    gender_terms: Optional[str] = None
    professions: Optional[str] = None
    stereotypes: Optional[str] = None
    asr_vocabulary: Optional[str] = None
    custom: List[str] = field(default_factory=list)


@dataclass
class LanguageConfig:
    """Complete language-specific configuration.
    
    Attributes:
        code: ISO 639-3 language code (e.g., 'fon', 'eng', 'fra')
        name: Full language name (e.g., 'Fongbe', 'English')
        family: Language family (e.g., 'Niger-Congo', 'Indo-European')
        script: Writing script (e.g., 'Latin', 'Arabic', 'Devanagari')
        direction: Text direction ('ltr' or 'rtl')
        tokenization: Tokenization configuration
        thresholds: Analysis thresholds
        analyzers: Analyzer configuration
        resources: Resource file paths
        plugins: List of custom plugin paths
    """
    code: str
    name: str
    family: str = "Unknown"
    script: str = "Latin"
    direction: str = "ltr"
    tokenization: TokenizationConfig = field(default_factory=TokenizationConfig)
    thresholds: ThresholdConfig = field(default_factory=ThresholdConfig)
    analyzers: AnalyzerConfig = field(default_factory=AnalyzerConfig)
    resources: ResourceConfig = field(default_factory=ResourceConfig)
    plugins: List[str] = field(default_factory=list)


@dataclass
class PackMetadata:
    """Metadata for a Language Pack.
    
    Attributes:
        version: Pack version (semantic versioning)
        author: Pack author name
        email: Author email
        license: License identifier (e.g., 'MIT', 'Apache-2.0')
        description: Brief description of the pack
        created: Creation date
        updated: Last update date
        contributors: List of contributor names
        status: Pack status ('stable', 'beta', 'alpha', 'experimental')
        coverage: Dictionary with coverage information
        dependencies: Dictionary with required dependencies
        references: List of reference URLs or DOIs
    """
    version: str
    author: str
    email: str
    license: str = "MIT"
    description: str = ""
    created: Optional[str] = None
    updated: Optional[str] = None
    contributors: List[str] = field(default_factory=list)
    status: str = "experimental"
    coverage: Dict[str, Any] = field(default_factory=dict)
    dependencies: Dict[str, str] = field(default_factory=dict)
    references: List[str] = field(default_factory=list)


@dataclass
class LanguagePack:
    """Complete Language Pack with configuration, metadata, and resources.
    
    Attributes:
        code: ISO 639-3 language code
        name: Language name
        config: Language configuration
        metadata: Pack metadata
        resources: Dictionary of loaded resources
        custom_analyzers: List of custom analyzer classes
        pack_path: Path to the language pack directory
    """
    code: str
    name: str
    config: LanguageConfig
    metadata: PackMetadata
    resources: Dict[str, Any] = field(default_factory=dict)
    custom_analyzers: List[Any] = field(default_factory=list)
    pack_path: Optional[Path] = None
    
    def get_resource(self, resource_name: str, default: Any = None) -> Any:
        """Get a resource with fallback to default.
        
        Args:
            resource_name: Name of the resource to retrieve
            default: Default value if resource not found
            
        Returns:
            Resource value or default
        """
        return self.resources.get(resource_name, default)
    
    def has_resource(self, resource_name: str) -> bool:
        """Check if a resource is available.
        
        Args:
            resource_name: Name of the resource to check
            
        Returns:
            True if resource exists, False otherwise
        """
        return resource_name in self.resources
    
    def list_resources(self) -> List[str]:
        """List all available resource names.
        
        Returns:
            List of resource names
        """
        return list(self.resources.keys())
