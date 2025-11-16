"""Validation schemas and functions for Language Pack configurations."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml


class ValidationError(Exception):
    """Exception raised for validation errors."""
    pass


class LanguagePackValidator:
    """Validator for Language Pack configurations and structures."""
    
    # Required fields in config.yaml
    REQUIRED_CONFIG_FIELDS = {
        "language": ["code", "name"],
    }
    
    # Valid values for specific fields
    VALID_DIRECTIONS = ["ltr", "rtl"]
    VALID_TOKENIZATION_METHODS = ["spacy", "nltk", "whitespace", "custom"]
    VALID_STATUSES = ["stable", "beta", "alpha", "experimental"]
    
    # Required fields in metadata.json
    REQUIRED_METADATA_FIELDS = ["version", "author", "email", "license"]
    
    @staticmethod
    def validate_config_yaml(config_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate the structure and content of config.yaml.
        
        Args:
            config_data: Parsed YAML configuration data
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required top-level sections
        if "language" not in config_data:
            errors.append("Missing required 'language' section")
            return False, errors
        
        # Validate language section
        language = config_data["language"]
        for field in LanguagePackValidator.REQUIRED_CONFIG_FIELDS["language"]:
            if field not in language:
                errors.append(f"Missing required field 'language.{field}'")
        
        # Validate language code format (ISO 639-3: 3 letters)
        if "code" in language:
            code = language["code"]
            if not isinstance(code, str) or len(code) != 3 or not code.isalpha():
                errors.append(
                    f"Invalid language code '{code}'. Must be 3-letter ISO 639-3 code"
                )
        
        # Validate direction if present
        if "direction" in language:
            direction = language["direction"]
            if direction not in LanguagePackValidator.VALID_DIRECTIONS:
                errors.append(
                    f"Invalid direction '{direction}'. Must be one of: "
                    f"{', '.join(LanguagePackValidator.VALID_DIRECTIONS)}"
                )
        
        # Validate tokenization section if present
        if "tokenization" in config_data:
            tokenization = config_data["tokenization"]
            if "method" in tokenization:
                method = tokenization["method"]
                if method not in LanguagePackValidator.VALID_TOKENIZATION_METHODS:
                    errors.append(
                        f"Invalid tokenization method '{method}'. Must be one of: "
                        f"{', '.join(LanguagePackValidator.VALID_TOKENIZATION_METHODS)}"
                    )
        
        # Validate thresholds if present
        if "thresholds" in config_data:
            threshold_errors = LanguagePackValidator._validate_thresholds(
                config_data["thresholds"]
            )
            errors.extend(threshold_errors)
        
        # Validate analyzers section if present
        if "analyzers" in config_data:
            analyzers = config_data["analyzers"]
            if "enabled" in analyzers and not isinstance(analyzers["enabled"], list):
                errors.append("'analyzers.enabled' must be a list")
            if "disabled" in analyzers and not isinstance(analyzers["disabled"], list):
                errors.append("'analyzers.disabled' must be a list")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def _validate_thresholds(thresholds: Dict[str, Any]) -> List[str]:
        """Validate threshold values.
        
        Args:
            thresholds: Threshold configuration dictionary
            
        Returns:
            List of error messages
        """
        errors = []
        
        # Validate structural thresholds
        if "structural" in thresholds:
            structural = thresholds["structural"]
            if "min_words" in structural and "max_words" in structural:
                if structural["min_words"] >= structural["max_words"]:
                    errors.append(
                        "structural.min_words must be less than structural.max_words"
                    )
            if "min_chars" in structural and "max_chars" in structural:
                if structural["min_chars"] >= structural["max_chars"]:
                    errors.append(
                        "structural.min_chars must be less than structural.max_chars"
                    )
        
        # Validate diversity thresholds
        if "diversity" in thresholds:
            diversity = thresholds["diversity"]
            if "target_ttr" in diversity:
                ttr = diversity["target_ttr"]
                if not (0.0 <= ttr <= 1.0):
                    errors.append(
                        f"diversity.target_ttr must be between 0.0 and 1.0, got {ttr}"
                    )
        
        # Validate domain thresholds
        if "domain" in thresholds:
            domain = thresholds["domain"]
            for field in ["min_representation", "max_representation", "balance_threshold"]:
                if field in domain:
                    value = domain[field]
                    if not (0.0 <= value <= 1.0):
                        errors.append(
                            f"domain.{field} must be between 0.0 and 1.0, got {value}"
                        )
        
        # Validate gender thresholds
        if "gender" in thresholds:
            gender = thresholds["gender"]
            if "target_ratio" in gender:
                ratio = gender["target_ratio"]
                if not isinstance(ratio, list) or len(ratio) != 2:
                    errors.append(
                        "gender.target_ratio must be a list of two values [min, max]"
                    )
                elif ratio[0] >= ratio[1]:
                    errors.append(
                        "gender.target_ratio[0] must be less than target_ratio[1]"
                    )
        
        return errors
    
    @staticmethod
    def validate_metadata_json(metadata: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate the structure and content of metadata.json.
        
        Args:
            metadata: Parsed JSON metadata
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required fields
        for field in LanguagePackValidator.REQUIRED_METADATA_FIELDS:
            if field not in metadata:
                errors.append(f"Missing required field '{field}'")
        
        # Validate version format (basic semantic versioning check)
        if "version" in metadata:
            version = metadata["version"]
            if not isinstance(version, str):
                errors.append("'version' must be a string")
            else:
                parts = version.split(".")
                if len(parts) != 3 or not all(p.isdigit() for p in parts):
                    errors.append(
                        f"Invalid version format '{version}'. "
                        "Must be semantic version (e.g., '1.0.0')"
                    )
        
        # Validate email format (basic check)
        if "email" in metadata:
            email = metadata["email"]
            if not isinstance(email, str) or "@" not in email:
                errors.append(f"Invalid email format '{email}'")
        
        # Validate status if present
        if "status" in metadata:
            status = metadata["status"]
            if status not in LanguagePackValidator.VALID_STATUSES:
                errors.append(
                    f"Invalid status '{status}'. Must be one of: "
                    f"{', '.join(LanguagePackValidator.VALID_STATUSES)}"
                )
        
        # Validate contributors is a list if present
        if "contributors" in metadata:
            if not isinstance(metadata["contributors"], list):
                errors.append("'contributors' must be a list")
        
        # Validate references is a list if present
        if "references" in metadata:
            if not isinstance(metadata["references"], list):
                errors.append("'references' must be a list")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_pack_structure(pack_path: Path) -> Tuple[bool, List[str]]:
        """Validate the directory structure of a Language Pack.
        
        Args:
            pack_path: Path to the language pack directory
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not pack_path.exists():
            errors.append(f"Language pack directory does not exist: {pack_path}")
            return False, errors
        
        if not pack_path.is_dir():
            errors.append(f"Language pack path is not a directory: {pack_path}")
            return False, errors
        
        # Check for required files
        config_file = pack_path / "config.yaml"
        metadata_file = pack_path / "metadata.json"
        
        if not config_file.exists():
            errors.append(f"Missing required file: config.yaml")
        
        if not metadata_file.exists():
            errors.append(f"Missing required file: metadata.json")
        
        # Check for resources directory (optional but recommended)
        resources_dir = pack_path / "resources"
        if not resources_dir.exists():
            # This is a warning, not an error
            pass
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_complete_pack(pack_path: Path) -> Tuple[bool, List[str], List[str]]:
        """Perform complete validation of a Language Pack.
        
        Args:
            pack_path: Path to the language pack directory
            
        Returns:
            Tuple of (is_valid, list_of_errors, list_of_warnings)
        """
        errors = []
        warnings = []
        
        # Validate directory structure
        structure_valid, structure_errors = LanguagePackValidator.validate_pack_structure(
            pack_path
        )
        errors.extend(structure_errors)
        
        if not structure_valid:
            return False, errors, warnings
        
        # Validate config.yaml
        config_file = pack_path / "config.yaml"
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)
            
            config_valid, config_errors = LanguagePackValidator.validate_config_yaml(
                config_data
            )
            errors.extend(config_errors)
        except yaml.YAMLError as e:
            errors.append(f"Invalid YAML in config.yaml: {e}")
        except Exception as e:
            errors.append(f"Error reading config.yaml: {e}")
        
        # Validate metadata.json
        metadata_file = pack_path / "metadata.json"
        try:
            import json
            with open(metadata_file, "r", encoding="utf-8") as f:
                metadata = json.load(f)
            
            metadata_valid, metadata_errors = LanguagePackValidator.validate_metadata_json(
                metadata
            )
            errors.extend(metadata_errors)
        except json.JSONDecodeError as e:
            errors.append(f"Invalid JSON in metadata.json: {e}")
        except Exception as e:
            errors.append(f"Error reading metadata.json: {e}")
        
        # Check for resources directory
        resources_dir = pack_path / "resources"
        if not resources_dir.exists():
            warnings.append(
                "No resources directory found. Pack will have limited functionality."
            )
        
        return len(errors) == 0, errors, warnings
