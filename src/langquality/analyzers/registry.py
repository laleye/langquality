"""Analyzer Registry for plugin system.

This module provides the AnalyzerRegistry class that manages analyzer discovery,
registration, and validation. It supports both built-in analyzers and custom
plugins loaded dynamically from directories.
"""

import importlib
import importlib.util
import inspect
import logging
from pathlib import Path
from typing import Dict, List, Optional, Type

from .base import Analyzer


logger = logging.getLogger(__name__)


class AnalyzerRegistry:
    """Registry for discovering and managing analyzers.
    
    The registry maintains a collection of analyzer classes and provides
    methods for registering, discovering, and retrieving analyzers. It
    supports both built-in analyzers and custom plugins.
    
    Attributes:
        _analyzers: Dictionary mapping analyzer names to analyzer classes
    """
    
    def __init__(self):
        """Initialize the analyzer registry."""
        self._analyzers: Dict[str, Type[Analyzer]] = {}
        self._load_builtin_analyzers()
    
    def _load_builtin_analyzers(self):
        """Load built-in analyzers from the analyzers package.
        
        This method automatically discovers and registers all built-in
        analyzer classes from the langquality.analyzers package.
        """
        try:
            # Import built-in analyzers
            from . import structural, linguistic, diversity, domain, gender_bias
            
            # Register each built-in analyzer
            builtin_modules = [structural, linguistic, diversity, domain, gender_bias]
            
            for module in builtin_modules:
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    # Check if it's an Analyzer subclass (but not Analyzer itself)
                    if (issubclass(obj, Analyzer) and 
                        obj != Analyzer and 
                        obj.__module__ == module.__name__):
                        
                        # Convert CamelCase to snake_case for analyzer name
                        # Remove 'Analyzer' suffix first
                        class_name = name.replace('Analyzer', '')
                        # Convert to snake_case
                        analyzer_name = self._camel_to_snake(class_name)
                        self._analyzers[analyzer_name] = obj
                        logger.debug(f"Registered built-in analyzer: {analyzer_name}")
        
        except ImportError as e:
            logger.warning(f"Failed to load some built-in analyzers: {e}")
    
    def _camel_to_snake(self, name: str) -> str:
        """Convert CamelCase to snake_case.
        
        Args:
            name: CamelCase string
            
        Returns:
            snake_case string
        """
        import re
        # Insert underscore before uppercase letters and convert to lowercase
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def register(self, name: str, analyzer_class: Type[Analyzer]):
        """Register an analyzer.
        
        Args:
            name: Name to register the analyzer under
            analyzer_class: Analyzer class to register
            
        Raises:
            ValueError: If the analyzer class is invalid
            TypeError: If analyzer_class is not a subclass of Analyzer
        """
        if not inspect.isclass(analyzer_class):
            raise TypeError(f"analyzer_class must be a class, got {type(analyzer_class)}")
        
        if not issubclass(analyzer_class, Analyzer):
            raise TypeError(f"{analyzer_class.__name__} must be a subclass of Analyzer")
        
        if not self.validate_analyzer(analyzer_class):
            raise ValueError(f"{analyzer_class.__name__} does not implement required interface")
        
        self._analyzers[name] = analyzer_class
        logger.info(f"Registered analyzer: {name} ({analyzer_class.__name__})")
    
    def discover_plugins(self, plugin_dir: str):
        """Discover and load analyzer plugins from directory.
        
        This method scans the specified directory for Python files containing
        Analyzer subclasses and automatically registers them.
        
        Args:
            plugin_dir: Path to directory containing plugin files
            
        Returns:
            Number of plugins successfully loaded
        """
        plugin_path = Path(plugin_dir)
        
        if not plugin_path.exists():
            logger.warning(f"Plugin directory does not exist: {plugin_dir}")
            return 0
        
        if not plugin_path.is_dir():
            logger.warning(f"Plugin path is not a directory: {plugin_dir}")
            return 0
        
        loaded_count = 0
        
        # Scan for Python files
        for file_path in plugin_path.glob("*.py"):
            if file_path.name.startswith("_"):
                continue  # Skip private files
            
            try:
                # Load the module dynamically
                module_name = f"langquality.plugins.{file_path.stem}"
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                
                if spec is None or spec.loader is None:
                    logger.warning(f"Could not load spec for {file_path}")
                    continue
                
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Find Analyzer subclasses in the module
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if (issubclass(obj, Analyzer) and 
                        obj != Analyzer and 
                        obj.__module__ == module_name):
                        
                        # Convert CamelCase to snake_case for analyzer name
                        class_name = name.replace('Analyzer', '')
                        analyzer_name = self._camel_to_snake(class_name)
                        
                        # Validate before registering
                        if self.validate_analyzer(obj):
                            self._analyzers[analyzer_name] = obj
                            loaded_count += 1
                            logger.info(f"Loaded plugin analyzer: {analyzer_name} from {file_path.name}")
                        else:
                            logger.warning(f"Plugin {name} in {file_path.name} does not implement required interface")
            
            except Exception as e:
                logger.error(f"Failed to load plugin from {file_path}: {e}")
        
        return loaded_count
    
    def get_analyzer(self, name: str) -> Type[Analyzer]:
        """Get an analyzer class by name.
        
        Args:
            name: Name of the analyzer to retrieve
            
        Returns:
            Analyzer class
            
        Raises:
            KeyError: If analyzer not found
        """
        if name not in self._analyzers:
            raise KeyError(f"Analyzer '{name}' not found. Available: {self.list_analyzers()}")
        
        return self._analyzers[name]
    
    def list_analyzers(self) -> List[str]:
        """List all registered analyzers.
        
        Returns:
            List of analyzer names
        """
        return sorted(self._analyzers.keys())
    
    def validate_analyzer(self, analyzer_class: Type[Analyzer]) -> bool:
        """Validate that an analyzer implements required interface.
        
        Checks that the analyzer class:
        - Is a subclass of Analyzer
        - Implements the analyze() method
        - Implements the get_requirements() method
        - Has name and version properties
        
        Args:
            analyzer_class: Analyzer class to validate
            
        Returns:
            True if analyzer is valid, False otherwise
        """
        if not inspect.isclass(analyzer_class):
            return False
        
        if not issubclass(analyzer_class, Analyzer):
            return False
        
        # Check for required methods
        required_methods = ['analyze', 'get_requirements', 'can_run']
        for method_name in required_methods:
            if not hasattr(analyzer_class, method_name):
                logger.warning(f"{analyzer_class.__name__} missing required method: {method_name}")
                return False
            
            method = getattr(analyzer_class, method_name)
            if not callable(method):
                logger.warning(f"{analyzer_class.__name__}.{method_name} is not callable")
                return False
        
        # Check for required properties
        required_properties = ['name', 'version']
        for prop_name in required_properties:
            if not hasattr(analyzer_class, prop_name):
                logger.warning(f"{analyzer_class.__name__} missing required property: {prop_name}")
                return False
        
        return True
    
    def has_analyzer(self, name: str) -> bool:
        """Check if an analyzer is registered.
        
        Args:
            name: Name of the analyzer to check
            
        Returns:
            True if analyzer is registered, False otherwise
        """
        return name in self._analyzers
    
    def unregister(self, name: str) -> bool:
        """Unregister an analyzer.
        
        Args:
            name: Name of the analyzer to unregister
            
        Returns:
            True if analyzer was unregistered, False if not found
        """
        if name in self._analyzers:
            del self._analyzers[name]
            logger.info(f"Unregistered analyzer: {name}")
            return True
        return False
    
    def clear(self):
        """Clear all registered analyzers."""
        self._analyzers.clear()
        logger.info("Cleared all registered analyzers")
