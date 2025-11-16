"""Tokenization system for language-agnostic text processing."""

from abc import ABC, abstractmethod
from typing import List, Optional
import logging


class Tokenizer(ABC):
    """Abstract base class for tokenizers.
    
    All tokenizer implementations must inherit from this class and implement
    the tokenize method.
    """
    
    def __init__(self, config: Optional[dict] = None):
        """Initialize tokenizer with optional configuration.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text into a list of tokens.
        
        Args:
            text: Input text to tokenize
            
        Returns:
            List of tokens
        """
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"


class WhitespaceTokenizer(Tokenizer):
    """Simple whitespace-based tokenizer.
    
    Splits text on whitespace characters. Fast and language-agnostic,
    suitable for languages with clear word boundaries.
    """
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text by splitting on whitespace.
        
        Args:
            text: Input text to tokenize
            
        Returns:
            List of tokens (words)
        """
        if not text:
            return []
        
        # Split on whitespace and filter empty strings
        tokens = [token for token in text.split() if token]
        return tokens


class SpacyTokenizer(Tokenizer):
    """Spacy-based tokenizer with linguistic awareness.
    
    Uses spaCy's language models for sophisticated tokenization that
    handles punctuation, contractions, and language-specific rules.
    """
    
    def __init__(self, config: Optional[dict] = None):
        """Initialize spaCy tokenizer.
        
        Args:
            config: Configuration dictionary with optional 'model' key
                   (e.g., {'model': 'fr_core_news_md'})
        """
        super().__init__(config)
        self.model_name = self.config.get('model', 'en_core_web_sm')
        self._nlp = None
    
    @property
    def nlp(self):
        """Lazy-load spaCy model."""
        if self._nlp is None:
            try:
                import spacy
                self._nlp = spacy.load(self.model_name)
                self.logger.info(f"Loaded spaCy model: {self.model_name}")
            except ImportError:
                raise ImportError(
                    "spaCy is required for SpacyTokenizer. "
                    "Install it with: pip install spacy"
                )
            except OSError:
                raise OSError(
                    f"spaCy model '{self.model_name}' not found. "
                    f"Download it with: python -m spacy download {self.model_name}"
                )
        return self._nlp
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text using spaCy.
        
        Args:
            text: Input text to tokenize
            
        Returns:
            List of tokens
        """
        if not text:
            return []
        
        doc = self.nlp(text)
        tokens = [token.text for token in doc]
        return tokens
    
    def __repr__(self) -> str:
        return f"SpacyTokenizer(model='{self.model_name}')"


class NLTKTokenizer(Tokenizer):
    """NLTK-based tokenizer.
    
    Uses NLTK's word tokenizer for language-aware tokenization.
    Requires NLTK to be installed and punkt tokenizer data downloaded.
    """
    
    def __init__(self, config: Optional[dict] = None):
        """Initialize NLTK tokenizer.
        
        Args:
            config: Configuration dictionary (currently unused)
        """
        super().__init__(config)
        self._ensure_nltk_data()
    
    def _ensure_nltk_data(self):
        """Ensure NLTK punkt tokenizer data is available."""
        try:
            import nltk
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                self.logger.info("Downloading NLTK punkt tokenizer data...")
                nltk.download('punkt', quiet=True)
        except ImportError:
            raise ImportError(
                "NLTK is required for NLTKTokenizer. "
                "Install it with: pip install nltk"
            )
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text using NLTK.
        
        Args:
            text: Input text to tokenize
            
        Returns:
            List of tokens
        """
        if not text:
            return []
        
        try:
            from nltk.tokenize import word_tokenize
            tokens = word_tokenize(text)
            return tokens
        except ImportError:
            raise ImportError(
                "NLTK is required for NLTKTokenizer. "
                "Install it with: pip install nltk"
            )


class CustomTokenizer(Tokenizer):
    """Custom tokenizer that can be configured with user-defined rules.
    
    Allows users to provide their own tokenization function or rules.
    """
    
    def __init__(self, config: Optional[dict] = None):
        """Initialize custom tokenizer.
        
        Args:
            config: Configuration dictionary with 'tokenize_fn' key
                   containing a callable that takes text and returns tokens
        """
        super().__init__(config)
        
        if 'tokenize_fn' not in self.config:
            raise ValueError(
                "CustomTokenizer requires 'tokenize_fn' in config"
            )
        
        self.tokenize_fn = self.config['tokenize_fn']
        
        if not callable(self.tokenize_fn):
            raise ValueError(
                "CustomTokenizer 'tokenize_fn' must be callable"
            )
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text using custom function.
        
        Args:
            text: Input text to tokenize
            
        Returns:
            List of tokens
        """
        if not text:
            return []
        
        return self.tokenize_fn(text)


def create_tokenizer(method: str, config: Optional[dict] = None) -> Tokenizer:
    """Factory function to create tokenizer instances.
    
    Args:
        method: Tokenization method ('whitespace', 'spacy', 'nltk', 'custom')
        config: Optional configuration dictionary
        
    Returns:
        Tokenizer instance
        
    Raises:
        ValueError: If method is not recognized
    """
    tokenizers = {
        'whitespace': WhitespaceTokenizer,
        'spacy': SpacyTokenizer,
        'nltk': NLTKTokenizer,
        'custom': CustomTokenizer,
    }
    
    method_lower = method.lower()
    
    if method_lower not in tokenizers:
        raise ValueError(
            f"Unknown tokenization method: {method}. "
            f"Available methods: {', '.join(tokenizers.keys())}"
        )
    
    tokenizer_class = tokenizers[method_lower]
    return tokenizer_class(config)
