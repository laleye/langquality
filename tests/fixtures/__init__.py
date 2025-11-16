"""Test fixtures for LangQuality test suite."""

from pathlib import Path


FIXTURES_DIR = Path(__file__).parent


def get_test_pack_path(pack_name: str) -> Path:
    """Get path to a test language pack.
    
    Args:
        pack_name: Name of the test pack (e.g., 'test_complete', 'test_minimal')
        
    Returns:
        Path to the language pack directory
    """
    return FIXTURES_DIR / "language_packs" / pack_name


def get_test_dataset_path(dataset_name: str) -> Path:
    """Get path to a test dataset.
    
    Args:
        dataset_name: Name of the dataset file (e.g., 'test_english.csv')
        
    Returns:
        Path to the dataset file
    """
    return FIXTURES_DIR / "datasets" / dataset_name


def get_test_plugin_dir() -> Path:
    """Get path to the test plugins directory.
    
    Returns:
        Path to the plugins directory
    """
    return FIXTURES_DIR / "plugins"


def get_language_packs_dir() -> Path:
    """Get path to the language packs directory.
    
    Returns:
        Path to the language_packs directory
    """
    return FIXTURES_DIR / "language_packs"
