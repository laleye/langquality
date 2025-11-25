"""Gender bias analyzer."""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import Analyzer


@dataclass
class GenderBiasMetrics:
    """Metrics for gender bias analysis."""
    
    masculine_count: int
    feminine_count: int
    gender_ratio: float  # F/M ratio
    stereotypes_detected: List[Dict]
    bias_score: float  # 0-1, 0 = balanced, 1 = highly biased
    total_gendered_mentions: int


class GenderBiasAnalyzer(Analyzer):
    """Analyzer for detecting and measuring gender bias in text.
    
    Supports configurable gender resources through language packs,
    allowing adaptation to different languages and cultural contexts.
    """
    
    def __init__(self, config: Any, language_pack: Optional[Any] = None):
        """Initialize the gender bias analyzer.
        
        Args:
            config: Configuration object with gender thresholds
            language_pack: Optional language pack with gender resources
        """
        super().__init__(config, language_pack)
        
        # Extract thresholds from config
        if hasattr(config, 'gender'):
            gender_config = config.gender
            self.target_ratio = gender_config.target_ratio
            self.check_stereotypes = gender_config.check_stereotypes
        else:
            # Fallback for old-style config
            self.target_ratio = getattr(config, 'target_ratio', (0.4, 0.6))
            self.check_stereotypes = getattr(config, 'check_stereotypes', True)
        
        # Load gender resources from language pack or fallback
        self.masculine_terms = self._load_masculine_terms()
        self.feminine_terms = self._load_feminine_terms()
        self.gendered_professions = self._load_gendered_professions()
        self.stereotype_patterns = self._load_stereotype_patterns()
    
    def _load_masculine_terms(self) -> List[str]:
        """Load masculine terms from language pack or fallback resources."""
        # Try to load from language pack first
        if self.language_pack and self.language_pack.has_resource('gender_terms'):
            gender_terms = self.language_pack.get_resource('gender_terms')
            if isinstance(gender_terms, dict) and 'masculine' in gender_terms:
                masc_data = gender_terms['masculine']
                terms = []
                # Handle both dict and list formats
                if isinstance(masc_data, dict):
                    terms.extend(masc_data.get('pronouns', []))
                    terms.extend(masc_data.get('articles', []))
                    terms.extend(masc_data.get('titles', []))
                elif isinstance(masc_data, list):
                    terms.extend(masc_data)
                return terms
        
        # Fallback to default resources
        try:
            resources_path = Path(__file__).parent.parent / "resources" / "gender_terms.json"
            with open(resources_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            terms = []
            terms.extend(data['masculine']['pronouns'])
            terms.extend(data['masculine']['articles'])
            terms.extend(data['masculine']['titles'])
            return terms
        except (FileNotFoundError, KeyError):
            self.logger.warning("Masculine terms not found, gender analysis will be limited")
            return []
    
    def _load_feminine_terms(self) -> List[str]:
        """Load feminine terms from language pack or fallback resources."""
        # Try to load from language pack first
        if self.language_pack and self.language_pack.has_resource('gender_terms'):
            gender_terms = self.language_pack.get_resource('gender_terms')
            if isinstance(gender_terms, dict) and 'feminine' in gender_terms:
                fem_data = gender_terms['feminine']
                terms = []
                # Handle both dict and list formats
                if isinstance(fem_data, dict):
                    terms.extend(fem_data.get('pronouns', []))
                    terms.extend(fem_data.get('articles', []))
                    terms.extend(fem_data.get('titles', []))
                elif isinstance(fem_data, list):
                    terms.extend(fem_data)
                return terms
        
        # Fallback to default resources
        try:
            resources_path = Path(__file__).parent.parent / "resources" / "gender_terms.json"
            with open(resources_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            terms = []
            terms.extend(data['feminine']['pronouns'])
            terms.extend(data['feminine']['articles'])
            terms.extend(data['feminine']['titles'])
            return terms
        except (FileNotFoundError, KeyError):
            self.logger.warning("Feminine terms not found, gender analysis will be limited")
            return []
    
    def _load_gendered_professions(self) -> List[Dict]:
        """Load gendered professions from language pack or fallback resources."""
        # Try to load from language pack first
        if self.language_pack and self.language_pack.has_resource('professions'):
            professions = self.language_pack.get_resource('professions')
            if isinstance(professions, dict) and 'professions' in professions:
                return professions['professions']
            elif isinstance(professions, list):
                return professions
        
        # Fallback to default resources
        try:
            resources_path = Path(__file__).parent.parent / "resources" / "gendered_professions.json"
            with open(resources_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data['professions']
        except (FileNotFoundError, KeyError):
            self.logger.warning("Gendered professions not found, profession analysis will be limited")
            return []
    
    def _load_stereotype_patterns(self) -> List[Dict]:
        """Load stereotype patterns from language pack or fallback resources."""
        # Only load if check_stereotypes is enabled
        if not self.check_stereotypes:
            return []
        
        # Try to load from language pack first
        if self.language_pack and self.language_pack.has_resource('stereotypes'):
            stereotypes = self.language_pack.get_resource('stereotypes')
            if isinstance(stereotypes, dict) and 'stereotypes' in stereotypes:
                patterns = stereotypes['stereotypes']
            elif isinstance(stereotypes, list):
                patterns = stereotypes
            else:
                self.logger.warning(f"Unexpected stereotype format from language pack: {type(stereotypes)}")
                patterns = []
            
            # Validate the loaded patterns
            if patterns:
                validated_patterns = []
                for pattern in patterns:
                    if isinstance(pattern, dict) and 'patterns' in pattern:
                        validated_patterns.append(pattern)
                    else:
                        self.logger.warning(f"Skipping invalid stereotype pattern: {pattern}")
                return validated_patterns
        
        # Fallback to default resources
        try:
            resources_path = Path(__file__).parent.parent / "resources" / "gender_stereotypes.json"
            with open(resources_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            patterns = data.get('stereotypes', [])
            
            # Validate the loaded patterns
            validated_patterns = []
            for pattern in patterns:
                if isinstance(pattern, dict) and 'patterns' in pattern:
                    validated_patterns.append(pattern)
                else:
                    self.logger.warning(f"Skipping invalid stereotype pattern: {pattern}")
            return validated_patterns
        except (FileNotFoundError, KeyError) as e:
            self.logger.warning(f"Gender stereotypes not found: {e}, stereotype detection will be disabled")
            return []
    
    def analyze(self, sentences) -> GenderBiasMetrics:
        """
        Analyze gender bias in the given sentences.
        
        Args:
            sentences: List of Sentence objects to analyze
            
        Returns:
            GenderBiasMetrics with bias analysis results
        """
        # Count gender mentions
        gender_counts = self.count_gender_mentions(sentences)
        
        # Compute gender ratio
        gender_ratio = self.compute_gender_ratio(gender_counts)
        
        # Detect stereotypes
        stereotypes = self.detect_stereotypes(sentences)
        
        # Calculate overall bias score
        bias_score = self._calculate_bias_score(gender_counts, stereotypes)
        
        total_mentions = gender_counts['masculine'] + gender_counts['feminine']
        
        return GenderBiasMetrics(
            masculine_count=gender_counts['masculine'],
            feminine_count=gender_counts['feminine'],
            gender_ratio=gender_ratio,
            stereotypes_detected=stereotypes,
            bias_score=bias_score,
            total_gendered_mentions=total_mentions
        )
    
    def count_gender_mentions(self, sentences) -> Dict[str, int]:
        """
        Count masculine and feminine mentions in sentences.
        
        Args:
            sentences: List of Sentence objects
            
        Returns:
            Dictionary with 'masculine' and 'feminine' counts
        """
        masculine_count = 0
        feminine_count = 0
        
        for sentence in sentences:
            text_lower = sentence.text.lower()
            
            # Count masculine terms
            for term in self.masculine_terms:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(term) + r'\b'
                masculine_count += len(re.findall(pattern, text_lower))
            
            # Count feminine terms
            for term in self.feminine_terms:
                pattern = r'\b' + re.escape(term) + r'\b'
                feminine_count += len(re.findall(pattern, text_lower))
            
            # Count gendered professions
            for profession in self.gendered_professions:
                if not profession['neutral']:
                    # Check for masculine form
                    masc_pattern = r'\b' + re.escape(profession['masculine']) + r'\b'
                    if re.search(masc_pattern, text_lower):
                        masculine_count += 1
                    
                    # Check for feminine form
                    fem_pattern = r'\b' + re.escape(profession['feminine']) + r'\b'
                    if re.search(fem_pattern, text_lower):
                        feminine_count += 1
        
        return {
            'masculine': masculine_count,
            'feminine': feminine_count
        }
    
    def compute_gender_ratio(self, counts: Dict[str, int]) -> float:
        """
        Compute the feminine/masculine ratio.
        
        Args:
            counts: Dictionary with 'masculine' and 'feminine' counts
            
        Returns:
            F/M ratio (0 if no masculine mentions)
        """
        if counts['masculine'] == 0:
            return float('inf') if counts['feminine'] > 0 else 0.0
        
        return counts['feminine'] / counts['masculine']
    
    def detect_stereotypes(self, sentences) -> List[Dict]:
        """
        Detect gender stereotypes in sentences.
        
        Args:
            sentences: List of Sentence objects
            
        Returns:
            List of detected stereotypes with details
        """
        detected_stereotypes = []
        
        for sentence in sentences:
            text_lower = sentence.text.lower()
            
            for stereotype in self.stereotype_patterns:
                # Validate stereotype structure
                if not isinstance(stereotype, dict):
                    self.logger.warning(f"Invalid stereotype format: expected dict, got {type(stereotype)}")
                    continue
                
                if 'patterns' not in stereotype:
                    self.logger.warning(f"Stereotype missing 'patterns' key: {stereotype}")
                    continue
                
                patterns = stereotype['patterns']
                if not isinstance(patterns, list):
                    self.logger.warning(f"Stereotype 'patterns' should be a list, got {type(patterns)}")
                    continue
                
                for pattern in patterns:
                    if re.search(pattern, text_lower):
                        detected_stereotypes.append({
                            'sentence': sentence.text,
                            'line_number': sentence.line_number,
                            'source_file': sentence.source_file,
                            'stereotype_type': stereotype.get('type', 'unknown'),
                            'description': stereotype.get('description', 'No description'),
                            'matched_pattern': pattern
                        })
                        break  # Only report once per sentence per stereotype type
        
        return detected_stereotypes
    
    def _calculate_bias_score(self, counts: Dict[str, int], stereotypes: List[Dict]) -> float:
        """
        Calculate overall bias score (0-1).
        
        Args:
            counts: Gender mention counts
            stereotypes: List of detected stereotypes
            
        Returns:
            Bias score between 0 (balanced) and 1 (highly biased)
        """
        # Component 1: Ratio imbalance (0-0.5)
        total = counts['masculine'] + counts['feminine']
        if total == 0:
            ratio_score = 0.0
        else:
            # Calculate deviation from 50/50 balance
            masculine_pct = counts['masculine'] / total
            # Distance from 0.5 (perfect balance), normalized to 0-0.5
            ratio_score = abs(masculine_pct - 0.5) * 1.0  # Max 0.5
        
        # Component 2: Stereotype presence (0-0.5)
        # Normalize by number of sentences (assuming ~1% stereotype rate is high)
        stereotype_score = min(len(stereotypes) * 0.1, 0.5)
        
        # Combine scores
        bias_score = ratio_score + stereotype_score
        
        # Ensure score is between 0 and 1
        return min(bias_score, 1.0)
    
    def get_requirements(self) -> List[str]:
        """Return list of required resources.
        
        The gender bias analyzer requires gender-specific resources
        to function properly.
        
        Returns:
            List of required resource names
        """
        # Gender terms and professions are required for meaningful analysis
        return ['gender_terms', 'professions']
