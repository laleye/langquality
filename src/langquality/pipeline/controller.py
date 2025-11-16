"""Pipeline controller for orchestrating analysis."""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from ..analyzers.base import Analyzer
from ..analyzers.registry import AnalyzerRegistry
from ..config.models import PipelineConfig
from ..data.models import Sentence
from ..language_packs.manager import LanguagePackManager
from ..language_packs.models import LanguagePack
from ..utils.exceptions import AnalysisError
from .results import AnalysisResults


logger = logging.getLogger(__name__)


class PipelineController:
    """Orchestrates the execution of analyzers with language pack support.
    
    The PipelineController manages the sequential execution of all enabled
    analyzers, handles errors gracefully with degradation, and aggregates 
    results into a single AnalysisResults object. It integrates with the
    AnalyzerRegistry for plugin support and LanguagePack system for 
    language-specific configurations.
    """
    
    def __init__(self, 
                 config: PipelineConfig,
                 language_pack: Optional[LanguagePack] = None,
                 analyzer_registry: Optional[AnalyzerRegistry] = None):
        """Initialize the pipeline controller.
        
        Args:
            config: Pipeline configuration specifying which analyzers to run
                   and their parameters
            language_pack: Optional LanguagePack with language-specific resources
            analyzer_registry: Optional AnalyzerRegistry for plugin support.
                             If None, creates a new registry with built-in analyzers.
        """
        self.config = config
        self.language_pack = language_pack
        self.registry = analyzer_registry or AnalyzerRegistry()
        self.skipped_analyzers: Dict[str, str] = {}  # Track skipped analyzers and reasons
        self.analyzers = self._initialize_analyzers()
    
    @classmethod
    def from_language_code(cls,
                          config: PipelineConfig,
                          language_code: str,
                          pack_manager: Optional[LanguagePackManager] = None,
                          analyzer_registry: Optional[AnalyzerRegistry] = None) -> 'PipelineController':
        """Create a PipelineController with automatic language pack loading.
        
        This is a convenience factory method that loads a language pack by code
        and creates a controller with it.
        
        Args:
            config: Pipeline configuration
            language_code: ISO 639-3 language code (e.g., 'fon', 'eng', 'fra')
            pack_manager: Optional LanguagePackManager. If None, creates a new one.
            analyzer_registry: Optional AnalyzerRegistry. If None, creates a new one.
            
        Returns:
            PipelineController instance with loaded language pack
            
        Raises:
            FileNotFoundError: If language pack not found
            ValidationError: If language pack validation fails
        """
        manager = pack_manager or LanguagePackManager()
        
        try:
            language_pack = manager.load_language_pack(language_code)
            logger.info(
                f"Loaded language pack '{language_code}' for pipeline controller"
            )
        except Exception as e:
            logger.warning(
                f"Failed to load language pack '{language_code}': {e}. "
                "Continuing without language pack (limited functionality)."
            )
            language_pack = None
        
        return cls(
            config=config,
            language_pack=language_pack,
            analyzer_registry=analyzer_registry
        )
    
    def _initialize_analyzers(self) -> Dict[str, Analyzer]:
        """Initialize all enabled analyzers based on configuration and language pack.
        
        This method:
        1. Determines which analyzers to enable from config or language pack
        2. Loads analyzer classes from the registry
        3. Checks resource availability for each analyzer
        4. Initializes analyzers that can run with available resources
        5. Tracks skipped analyzers with reasons for graceful degradation
        
        Returns:
            Dictionary mapping analyzer names to analyzer instances
        """
        analyzers = {}
        
        # Determine which analyzers to enable
        if self.language_pack:
            # Use language pack configuration if available
            enabled_list = self.language_pack.config.analyzers.enabled
            disabled_list = self.language_pack.config.analyzers.disabled
            
            # Filter out disabled analyzers
            enabled_analyzers = [a for a in enabled_list if a not in disabled_list]
            
            logger.info(
                f"Using language pack '{self.language_pack.code}' analyzer configuration: "
                f"enabled={enabled_analyzers}"
            )
        else:
            # Fall back to pipeline config
            enable_all = "all" in self.config.enable_analyzers
            
            if enable_all:
                # Enable all registered analyzers
                enabled_analyzers = self.registry.list_analyzers()
                logger.info("Enabling all registered analyzers")
            else:
                enabled_analyzers = self.config.enable_analyzers
                logger.info(f"Enabling analyzers from config: {enabled_analyzers}")
        
        # Initialize each enabled analyzer
        for analyzer_name in enabled_analyzers:
            try:
                # Get analyzer class from registry
                if not self.registry.has_analyzer(analyzer_name):
                    logger.warning(
                        f"Analyzer '{analyzer_name}' not found in registry. "
                        f"Available: {self.registry.list_analyzers()}"
                    )
                    self.skipped_analyzers[analyzer_name] = "Not found in registry"
                    continue
                
                analyzer_class = self.registry.get_analyzer(analyzer_name)
                
                # Create analyzer instance with language pack
                analyzer = analyzer_class(
                    config=self.config.analysis,
                    language_pack=self.language_pack
                )
                
                # Check if analyzer can run with available resources
                can_run, reason = analyzer.can_run()
                
                if can_run:
                    analyzers[analyzer_name] = analyzer
                    logger.info(
                        f"Initialized {analyzer_class.__name__} "
                        f"(version {analyzer.version})"
                    )
                else:
                    # Track why analyzer was skipped
                    self.skipped_analyzers[analyzer_name] = reason
                    logger.warning(
                        f"Skipping {analyzer_name}: {reason}. "
                        "Analysis will continue without this analyzer."
                    )
            
            except Exception as e:
                logger.error(
                    f"Failed to initialize {analyzer_name}: {e}",
                    exc_info=True
                )
                self.skipped_analyzers[analyzer_name] = f"Initialization error: {str(e)}"
        
        # Log summary
        if analyzers:
            logger.info(
                f"Successfully initialized {len(analyzers)} analyzer(s): "
                f"{list(analyzers.keys())}"
            )
        
        if self.skipped_analyzers:
            logger.warning(
                f"Skipped {len(self.skipped_analyzers)} analyzer(s): "
                f"{list(self.skipped_analyzers.keys())}"
            )
        
        return analyzers
    
    def run(self, sentences: List[Sentence]) -> AnalysisResults:
        """Run the analysis pipeline on the given sentences.
        
        Executes all enabled analyzers sequentially with graceful degradation.
        If an analyzer fails, the error is logged and the pipeline continues 
        with remaining analyzers. Provides clear feedback about skipped and
        failed analyzers.
        
        Args:
            sentences: List of sentences to analyze
            
        Returns:
            AnalysisResults containing metrics from all successful analyzers
            
        Raises:
            AnalysisError: If no analyzers are enabled or all analyzers fail
        """
        # Check if any analyzers are available
        if not self.analyzers and not self.skipped_analyzers:
            raise AnalysisError(
                "No analyzers enabled in pipeline configuration. "
                "Please check your configuration or language pack settings."
            )
        
        if not self.analyzers:
            # All analyzers were skipped
            skipped_reasons = "\n".join(
                f"  - {name}: {reason}" 
                for name, reason in self.skipped_analyzers.items()
            )
            raise AnalysisError(
                f"All analyzers were skipped due to missing resources:\n{skipped_reasons}\n"
                "Please provide a language pack with required resources or use "
                "language-agnostic analyzers."
            )
        
        if not sentences:
            logger.warning("No sentences provided for analysis")
        
        # Log pipeline start with context
        logger.info(f"Starting pipeline analysis with {len(sentences)} sentences")
        if self.language_pack:
            logger.info(
                f"Using language pack: {self.language_pack.name} "
                f"(v{self.language_pack.metadata.version})"
            )
        logger.info(f"Active analyzers: {list(self.analyzers.keys())}")
        
        # Log skipped analyzers as warnings
        if self.skipped_analyzers:
            logger.warning(
                f"Skipped {len(self.skipped_analyzers)} analyzer(s) due to missing resources:"
            )
            for name, reason in self.skipped_analyzers.items():
                logger.warning(f"  - {name}: {reason}")
        
        # Initialize results dictionary
        results = {
            "structural": None,
            "linguistic": None,
            "diversity": None,
            "domain": None,
            "gender_bias": None
        }
        
        # Track execution statistics
        successful_count = 0
        failed_count = 0
        
        # Run each analyzer with error handling
        for analyzer_name, analyzer in self.analyzers.items():
            try:
                logger.info(f"Running {analyzer_name} analyzer...")
                metrics = analyzer.analyze(sentences)
                results[analyzer_name] = metrics
                successful_count += 1
                logger.info(f"Completed {analyzer_name} analyzer successfully")
            except Exception as e:
                failed_count += 1
                logger.error(
                    f"Analyzer '{analyzer_name}' failed with error: {e}",
                    exc_info=True
                )
                # Continue with other analyzers (graceful degradation)
                results[analyzer_name] = None
        
        # Check if at least one analyzer succeeded
        if successful_count == 0:
            raise AnalysisError(
                f"All {failed_count} active analyzer(s) failed during execution. "
                "Check logs for details."
            )
        
        # Create aggregated results
        analysis_results = AnalysisResults(
            structural=results.get("structural"),
            linguistic=results.get("linguistic"),
            diversity=results.get("diversity"),
            domain=results.get("domain"),
            gender_bias=results.get("gender_bias"),
            timestamp=datetime.now(),
            config_used=self.config
        )
        
        # Log completion summary
        logger.info(
            f"Pipeline analysis completed: {successful_count} successful, "
            f"{failed_count} failed, {len(self.skipped_analyzers)} skipped"
        )
        
        return analysis_results
    
    def get_skipped_analyzers(self) -> Dict[str, str]:
        """Get information about analyzers that were skipped.
        
        Returns:
            Dictionary mapping analyzer names to skip reasons
        """
        return self.skipped_analyzers.copy()
    
    def get_active_analyzers(self) -> List[str]:
        """Get list of active analyzer names.
        
        Returns:
            List of analyzer names that are initialized and ready to run
        """
        return list(self.analyzers.keys())
    
    def get_fallback_suggestions(self) -> Dict[str, str]:
        """Get suggestions for language-agnostic alternatives to skipped analyzers.
        
        Provides helpful suggestions when analyzers are skipped due to missing
        resources, recommending language-agnostic alternatives or actions.
        
        Returns:
            Dictionary mapping skipped analyzer names to suggestion messages
        """
        suggestions = {}
        
        # Define language-agnostic alternatives
        language_agnostic_analyzers = {
            'structural', 'domain', 'diversity'
        }
        
        for analyzer_name, reason in self.skipped_analyzers.items():
            if 'resource' in reason.lower():
                # Analyzer was skipped due to missing resources
                if analyzer_name == 'gender_bias':
                    suggestions[analyzer_name] = (
                        "Gender bias analysis requires language-specific resources "
                        "(gender_terms, professions). Consider creating a language pack "
                        "with these resources, or focus on language-agnostic metrics "
                        "like structural and diversity analysis."
                    )
                elif analyzer_name == 'linguistic':
                    suggestions[analyzer_name] = (
                        "Linguistic analysis works best with a language pack containing "
                        "a frequency lexicon. Basic readability metrics are still available "
                        "without resources. Consider using structural and diversity analyzers "
                        "for language-agnostic quality assessment."
                    )
                else:
                    # Generic suggestion
                    suggestions[analyzer_name] = (
                        f"Consider providing a language pack with required resources, "
                        f"or use language-agnostic analyzers: "
                        f"{', '.join(sorted(language_agnostic_analyzers))}"
                    )
            else:
                # Other reasons (initialization error, not found, etc.)
                suggestions[analyzer_name] = (
                    f"Check that the analyzer is properly installed and configured. "
                    f"Available analyzers: {', '.join(self.registry.list_analyzers())}"
                )
        
        return suggestions
    
    def print_analysis_summary(self):
        """Print a summary of the pipeline configuration and status.
        
        Useful for debugging and understanding which analyzers are active,
        skipped, and why. Includes suggestions for improving coverage.
        """
        print("\n" + "="*70)
        print("PIPELINE ANALYSIS SUMMARY")
        print("="*70)
        
        if self.language_pack:
            print(f"\nLanguage Pack: {self.language_pack.name} (v{self.language_pack.metadata.version})")
            print(f"Language Code: {self.language_pack.code}")
            print(f"Available Resources: {', '.join(self.language_pack.list_resources())}")
        else:
            print("\nLanguage Pack: None (using language-agnostic analyzers only)")
        
        print(f"\nActive Analyzers ({len(self.analyzers)}):")
        for name in sorted(self.analyzers.keys()):
            analyzer = self.analyzers[name]
            requirements = analyzer.get_requirements()
            req_str = f" [requires: {', '.join(requirements)}]" if requirements else " [no requirements]"
            print(f"  ✓ {name}{req_str}")
        
        if self.skipped_analyzers:
            print(f"\nSkipped Analyzers ({len(self.skipped_analyzers)}):")
            suggestions = self.get_fallback_suggestions()
            for name in sorted(self.skipped_analyzers.keys()):
                reason = self.skipped_analyzers[name]
                print(f"  ✗ {name}: {reason}")
                if name in suggestions:
                    print(f"    → Suggestion: {suggestions[name]}")
        
        print("\n" + "="*70 + "\n")
