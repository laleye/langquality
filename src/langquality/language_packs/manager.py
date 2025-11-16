"""Language Pack Manager for loading and managing language packs."""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

from .models import (
    AnalyzerConfig,
    DiversityThresholds,
    DomainThresholds,
    GenderThresholds,
    LanguageConfig,
    LanguagePack,
    LinguisticThresholds,
    PackMetadata,
    ResourceConfig,
    StructuralThresholds,
    ThresholdConfig,
    TokenizationConfig,
)
from .validation import LanguagePackValidator, ValidationError


logger = logging.getLogger(__name__)


class LanguagePackManager:
    """Manages language packs and configurations."""
    
    def __init__(self, packs_directory: Optional[Path] = None):
        """Initialize the Language Pack Manager.
        
        Args:
            packs_directory: Path to directory containing language packs.
                           If None, uses default location.
        """
        if packs_directory is None:
            # Default to language_packs directory in the package
            self.packs_directory = Path(__file__).parent / "packs"
        else:
            self.packs_directory = Path(packs_directory)
        
        self._cache: Dict[str, LanguagePack] = {}
        self.validator = LanguagePackValidator()
    
    def load_language_pack(self, language_code: str, 
                          validate: bool = True) -> LanguagePack:
        """Load a language pack by ISO 639-3 code.
        
        Args:
            language_code: ISO 639-3 language code (e.g., 'fon', 'eng', 'fra')
            validate: Whether to validate the pack before loading
            
        Returns:
            Loaded LanguagePack instance
            
        Raises:
            FileNotFoundError: If language pack directory not found
            ValidationError: If pack validation fails
        """
        # Check cache first
        if language_code in self._cache:
            logger.debug(f"Loading language pack '{language_code}' from cache")
            return self._cache[language_code]
        
        # Find pack directory
        pack_path = self.packs_directory / language_code
        if not pack_path.exists():
            raise FileNotFoundError(
                f"Language pack '{language_code}' not found at {pack_path}"
            )
        
        # Validate pack structure if requested
        if validate:
            is_valid, errors, warnings = self.validator.validate_complete_pack(pack_path)
            
            for warning in warnings:
                logger.warning(f"Language pack '{language_code}': {warning}")
            
            if not is_valid:
                error_msg = f"Language pack '{language_code}' validation failed:\n"
                error_msg += "\n".join(f"  - {error}" for error in errors)
                raise ValidationError(error_msg)
        
        # Load configuration
        config = self._load_config(pack_path)
        
        # Load metadata
        metadata = self._load_metadata(pack_path)
        
        # Load resources
        resources = self._load_resources(pack_path, config.resources)
        
        # Create LanguagePack instance
        pack = LanguagePack(
            code=language_code,
            name=config.name,
            config=config,
            metadata=metadata,
            resources=resources,
            pack_path=pack_path,
        )
        
        # Cache the pack
        self._cache[language_code] = pack
        
        logger.info(f"Successfully loaded language pack '{language_code}'")
        return pack
    
    def _load_config(self, pack_path: Path) -> LanguageConfig:
        """Load configuration from config.yaml.
        
        Args:
            pack_path: Path to language pack directory
            
        Returns:
            LanguageConfig instance
        """
        config_file = pack_path / "config.yaml"
        
        with open(config_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        
        # Parse language section
        lang_data = data.get("language", {})
        
        # Parse tokenization section
        tok_data = data.get("tokenization", {})
        tokenization = TokenizationConfig(
            method=tok_data.get("method", "whitespace"),
            model=tok_data.get("model"),
            custom_rules=tok_data.get("custom_rules", []),
        )
        
        # Parse thresholds section
        thresh_data = data.get("thresholds", {})
        thresholds = self._parse_thresholds(thresh_data)
        
        # Parse analyzers section
        analyzer_data = data.get("analyzers", {})
        analyzers = AnalyzerConfig(
            enabled=analyzer_data.get("enabled", [
                "structural", "linguistic", "diversity", "domain"
            ]),
            disabled=analyzer_data.get("disabled", []),
        )
        
        # Parse resources section
        res_data = data.get("resources", {})
        resources = ResourceConfig(
            lexicon=res_data.get("lexicon"),
            stopwords=res_data.get("stopwords"),
            gender_terms=res_data.get("gender_terms"),
            professions=res_data.get("professions"),
            stereotypes=res_data.get("stereotypes"),
            asr_vocabulary=res_data.get("asr_vocabulary"),
            custom=res_data.get("custom", []),
        )
        
        # Create LanguageConfig
        config = LanguageConfig(
            code=lang_data["code"],
            name=lang_data["name"],
            family=lang_data.get("family", "Unknown"),
            script=lang_data.get("script", "Latin"),
            direction=lang_data.get("direction", "ltr"),
            tokenization=tokenization,
            thresholds=thresholds,
            analyzers=analyzers,
            resources=resources,
            plugins=data.get("plugins", []),
        )
        
        return config
    
    def _parse_thresholds(self, thresh_data: Dict) -> ThresholdConfig:
        """Parse threshold configuration from YAML data.
        
        Args:
            thresh_data: Threshold data from YAML
            
        Returns:
            ThresholdConfig instance
        """
        structural = None
        if "structural" in thresh_data:
            s = thresh_data["structural"]
            structural = StructuralThresholds(
                min_words=s.get("min_words", 3),
                max_words=s.get("max_words", 20),
                min_chars=s.get("min_chars", 10),
                max_chars=s.get("max_chars", 200),
            )
        
        linguistic = None
        if "linguistic" in thresh_data:
            l = thresh_data["linguistic"]
            linguistic = LinguisticThresholds(
                max_readability_score=l.get("max_readability_score", 60.0),
                enable_pos_tagging=l.get("enable_pos_tagging", True),
                enable_dependency_parsing=l.get("enable_dependency_parsing", False),
            )
        
        diversity = None
        if "diversity" in thresh_data:
            d = thresh_data["diversity"]
            diversity = DiversityThresholds(
                target_ttr=d.get("target_ttr", 0.6),
                min_unique_words=d.get("min_unique_words", 100),
                check_duplicates=d.get("check_duplicates", True),
            )
        
        domain = None
        if "domain" in thresh_data:
            dom = thresh_data["domain"]
            domain = DomainThresholds(
                min_representation=dom.get("min_representation", 0.10),
                max_representation=dom.get("max_representation", 0.30),
                balance_threshold=dom.get("balance_threshold", 0.15),
            )
        
        gender = None
        if "gender" in thresh_data:
            g = thresh_data["gender"]
            target_ratio = g.get("target_ratio", [0.4, 0.6])
            gender = GenderThresholds(
                target_ratio=tuple(target_ratio),
                check_stereotypes=g.get("check_stereotypes", True),
            )
        
        return ThresholdConfig(
            structural=structural,
            linguistic=linguistic,
            diversity=diversity,
            domain=domain,
            gender=gender,
        )
    
    def _load_metadata(self, pack_path: Path) -> PackMetadata:
        """Load metadata from metadata.json.
        
        Args:
            pack_path: Path to language pack directory
            
        Returns:
            PackMetadata instance
        """
        metadata_file = pack_path / "metadata.json"
        
        with open(metadata_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        metadata = PackMetadata(
            version=data["version"],
            author=data["author"],
            email=data["email"],
            license=data.get("license", "MIT"),
            description=data.get("description", ""),
            created=data.get("created"),
            updated=data.get("updated"),
            contributors=data.get("contributors", []),
            status=data.get("status", "experimental"),
            coverage=data.get("coverage", {}),
            dependencies=data.get("dependencies", {}),
            references=data.get("references", []),
        )
        
        return metadata
    
    def _load_resources(self, pack_path: Path, 
                       resource_config: ResourceConfig) -> Dict[str, any]:
        """Load resource files with fallback handling.
        
        Args:
            pack_path: Path to language pack directory
            resource_config: Resource configuration
            
        Returns:
            Dictionary of loaded resources
        """
        resources = {}
        resources_dir = pack_path / "resources"
        
        if not resources_dir.exists():
            logger.warning(
                f"Resources directory not found at {resources_dir}. "
                "Pack will have limited functionality."
            )
            return resources
        
        # Load lexicon
        if resource_config.lexicon:
            lexicon_path = resources_dir / resource_config.lexicon
            resources["lexicon"] = self._load_text_resource(
                lexicon_path, "lexicon"
            )
        
        # Load stopwords
        if resource_config.stopwords:
            stopwords_path = resources_dir / resource_config.stopwords
            resources["stopwords"] = self._load_text_resource(
                stopwords_path, "stopwords"
            )
        
        # Load gender terms
        if resource_config.gender_terms:
            gender_path = resources_dir / resource_config.gender_terms
            resources["gender_terms"] = self._load_json_resource(
                gender_path, "gender_terms"
            )
        
        # Load professions
        if resource_config.professions:
            prof_path = resources_dir / resource_config.professions
            resources["professions"] = self._load_json_resource(
                prof_path, "professions"
            )
        
        # Load stereotypes
        if resource_config.stereotypes:
            stereo_path = resources_dir / resource_config.stereotypes
            resources["stereotypes"] = self._load_json_resource(
                stereo_path, "stereotypes"
            )
        
        # Load ASR vocabulary
        if resource_config.asr_vocabulary:
            asr_path = resources_dir / resource_config.asr_vocabulary
            resources["asr_vocabulary"] = self._load_text_resource(
                asr_path, "asr_vocabulary"
            )
        
        # Load custom resources
        for custom_path in resource_config.custom:
            custom_full_path = resources_dir / custom_path
            resource_name = Path(custom_path).stem
            
            if custom_full_path.suffix == ".json":
                resources[resource_name] = self._load_json_resource(
                    custom_full_path, resource_name
                )
            else:
                resources[resource_name] = self._load_text_resource(
                    custom_full_path, resource_name
                )
        
        return resources
    
    def _load_text_resource(self, path: Path, name: str) -> Optional[List[str]]:
        """Load a text resource file.
        
        Args:
            path: Path to resource file
            name: Resource name for logging
            
        Returns:
            List of lines or None if file not found
        """
        if not path.exists():
            logger.warning(f"Resource file not found: {name} at {path}")
            return None
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
            logger.debug(f"Loaded {len(lines)} lines from {name}")
            return lines
        except Exception as e:
            logger.error(f"Error loading resource {name}: {e}")
            return None
    
    def _load_json_resource(self, path: Path, name: str) -> Optional[Dict]:
        """Load a JSON resource file.
        
        Args:
            path: Path to resource file
            name: Resource name for logging
            
        Returns:
            Parsed JSON data or None if file not found
        """
        if not path.exists():
            logger.warning(f"Resource file not found: {name} at {path}")
            return None
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.debug(f"Loaded JSON resource: {name}")
            return data
        except Exception as e:
            logger.error(f"Error loading resource {name}: {e}")
            return None
    
    def list_available_packs(self) -> List[str]:
        """List all installed language packs.
        
        Returns:
            List of language codes for available packs
        """
        if not self.packs_directory.exists():
            logger.warning(f"Packs directory not found: {self.packs_directory}")
            return []
        
        packs = []
        for item in self.packs_directory.iterdir():
            if item.is_dir() and not item.name.startswith("_"):
                # Check if it has required files
                if (item / "config.yaml").exists() and (item / "metadata.json").exists():
                    packs.append(item.name)
        
        return sorted(packs)
    
    def validate_pack(self, pack_path: Path) -> Tuple[bool, List[str], List[str]]:
        """Validate a language pack structure and content.
        
        Args:
            pack_path: Path to language pack directory
            
        Returns:
            Tuple of (is_valid, list_of_errors, list_of_warnings)
        """
        return self.validator.validate_complete_pack(pack_path)
    
    def get_pack_info(self, language_code: str) -> Optional[Dict]:
        """Get information about a language pack without fully loading it.
        
        Args:
            language_code: ISO 639-3 language code
            
        Returns:
            Dictionary with pack information or None if not found
        """
        pack_path = self.packs_directory / language_code
        if not pack_path.exists():
            return None
        
        try:
            # Load metadata only
            metadata_file = pack_path / "metadata.json"
            with open(metadata_file, "r", encoding="utf-8") as f:
                metadata = json.load(f)
            
            # Load basic config info
            config_file = pack_path / "config.yaml"
            with open(config_file, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            
            return {
                "code": language_code,
                "name": config.get("language", {}).get("name", "Unknown"),
                "version": metadata.get("version", "Unknown"),
                "status": metadata.get("status", "Unknown"),
                "author": metadata.get("author", "Unknown"),
                "description": metadata.get("description", ""),
            }
        except Exception as e:
            logger.error(f"Error reading pack info for '{language_code}': {e}")
            return None
    
    def clear_cache(self):
        """Clear the language pack cache."""
        self._cache.clear()
        logger.debug("Language pack cache cleared")
