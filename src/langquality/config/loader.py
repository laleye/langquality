"""Configuration loader for the analysis pipeline."""

from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from .models import AnalysisConfig, PipelineConfig
from ..utils.exceptions import ConfigurationError


def load_config(config_path: Optional[str] = None) -> PipelineConfig:
    """Load configuration from YAML file or use defaults.
    
    Args:
        config_path: Path to YAML configuration file. If None, uses default config.
        
    Returns:
        PipelineConfig object with loaded configuration
        
    Raises:
        ConfigurationError: If configuration file cannot be loaded or is invalid
    """
    if config_path is None:
        # Use default configuration
        return _create_default_config()
    
    try:
        config_file = Path(config_path)
        if not config_file.exists():
            raise ConfigurationError(f"Configuration file not found: {config_path}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        if config_data is None:
            raise ConfigurationError(f"Configuration file is empty: {config_path}")
        
        return _parse_config(config_data)
        
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Invalid YAML in configuration file: {e}")
    except Exception as e:
        raise ConfigurationError(f"Failed to load configuration: {e}")


def _create_default_config() -> PipelineConfig:
    """Create a default pipeline configuration.
    
    Returns:
        PipelineConfig with default values
    """
    return PipelineConfig(
        analysis=AnalysisConfig(),
        input_directory="data/",
        output_directory="output/"
    )


def _parse_config(config_data: Dict[str, Any]) -> PipelineConfig:
    """Parse configuration dictionary into PipelineConfig object.
    
    Args:
        config_data: Dictionary containing configuration data
        
    Returns:
        PipelineConfig object
        
    Raises:
        ConfigurationError: If configuration data is invalid
    """
    try:
        # Parse analysis configuration
        analysis_data = config_data.get('analysis', {})
        analysis_config = AnalysisConfig(
            min_words=analysis_data.get('min_words', 3),
            max_words=analysis_data.get('max_words', 20),
            min_readability_score=analysis_data.get('min_readability_score', 0.0),
            max_readability_score=analysis_data.get('max_readability_score', 60.0),
            target_ttr=analysis_data.get('target_ttr', 0.6),
            min_domain_representation=analysis_data.get('min_domain_representation', 0.10),
            max_domain_representation=analysis_data.get('max_domain_representation', 0.30),
            target_gender_ratio=tuple(analysis_data.get('target_gender_ratio', [0.4, 0.6])),
            jargon_terms=analysis_data.get('jargon_terms', []),
            reference_vocabulary=analysis_data.get('reference_vocabulary')
        )
        
        # Validate analysis configuration
        _validate_analysis_config(analysis_config)
        
        # Parse pipeline configuration
        pipeline_config = PipelineConfig(
            analysis=analysis_config,
            input_directory=config_data.get('input_directory', 'data/'),
            output_directory=config_data.get('output_directory', 'output/'),
            enable_analyzers=config_data.get('enable_analyzers', ['all']),
            language=config_data.get('language', 'fr')
        )
        
        # Validate pipeline configuration
        _validate_pipeline_config(pipeline_config)
        
        return pipeline_config
        
    except (KeyError, TypeError, ValueError) as e:
        raise ConfigurationError(f"Invalid configuration format: {e}")


def _validate_analysis_config(config: AnalysisConfig) -> None:
    """Validate analysis configuration parameters.
    
    Args:
        config: AnalysisConfig to validate
        
    Raises:
        ConfigurationError: If configuration is invalid
    """
    # Validate word count thresholds
    if config.min_words < 1:
        raise ConfigurationError("min_words must be at least 1")
    
    if config.max_words < config.min_words:
        raise ConfigurationError("max_words must be greater than or equal to min_words")
    
    # Validate readability scores
    if config.min_readability_score < 0:
        raise ConfigurationError("min_readability_score must be non-negative")
    
    if config.max_readability_score < config.min_readability_score:
        raise ConfigurationError("max_readability_score must be greater than or equal to min_readability_score")
    
    # Validate TTR
    if not 0 <= config.target_ttr <= 1:
        raise ConfigurationError("target_ttr must be between 0 and 1")
    
    # Validate domain representation
    if not 0 <= config.min_domain_representation <= 1:
        raise ConfigurationError("min_domain_representation must be between 0 and 1")
    
    if not 0 <= config.max_domain_representation <= 1:
        raise ConfigurationError("max_domain_representation must be between 0 and 1")
    
    if config.max_domain_representation < config.min_domain_representation:
        raise ConfigurationError("max_domain_representation must be greater than or equal to min_domain_representation")
    
    # Validate gender ratio
    if len(config.target_gender_ratio) != 2:
        raise ConfigurationError("target_gender_ratio must be a tuple of two values")
    
    min_ratio, max_ratio = config.target_gender_ratio
    if not 0 <= min_ratio <= 1 or not 0 <= max_ratio <= 1:
        raise ConfigurationError("target_gender_ratio values must be between 0 and 1")
    
    if max_ratio < min_ratio:
        raise ConfigurationError("target_gender_ratio max must be greater than or equal to min")


def _validate_pipeline_config(config: PipelineConfig) -> None:
    """Validate pipeline configuration parameters.
    
    Args:
        config: PipelineConfig to validate
        
    Raises:
        ConfigurationError: If configuration is invalid
    """
    # Validate input directory
    if not config.input_directory:
        raise ConfigurationError("input_directory cannot be empty")
    
    # Validate output directory
    if not config.output_directory:
        raise ConfigurationError("output_directory cannot be empty")
    
    # Validate language
    if config.language not in ['fr', 'en']:  # Can be extended
        raise ConfigurationError(f"Unsupported language: {config.language}")
    
    # Validate enable_analyzers
    if not config.enable_analyzers:
        raise ConfigurationError("enable_analyzers cannot be empty")
    
    valid_analyzers = ['all', 'structural', 'linguistic', 'diversity', 'domain', 'gender_bias']
    for analyzer in config.enable_analyzers:
        if analyzer not in valid_analyzers:
            raise ConfigurationError(f"Invalid analyzer name: {analyzer}. Valid options: {valid_analyzers}")
