"""Integration tests for pipeline with language packs."""

import pytest
import tempfile
import shutil
from pathlib import Path

from src.langquality.language_packs.manager import LanguagePackManager
from src.langquality.analyzers.registry import AnalyzerRegistry
from src.langquality.data.generic_loader import GenericDataLoader
from src.langquality.pipeline.controller import PipelineController
from tests.fixtures import (
    get_language_packs_dir,
    get_test_dataset_path,
    get_test_plugin_dir
)


class TestPipelineWithLanguagePacks:
    """Integration tests for complete pipeline with language packs."""
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def pack_manager(self):
        """Create language pack manager."""
        return LanguagePackManager(get_language_packs_dir())
    
    def test_pipeline_with_complete_pack(self, pack_manager, temp_output_dir):
        """Test pipeline execution with complete language pack."""
        # Load language pack
        pack = pack_manager.load_language_pack("test_complete")
        
        # Load data
        dataset_path = get_test_dataset_path("test_english.csv")
        loader = GenericDataLoader(pack)
        sentences = loader.load_from_csv(str(dataset_path))
        
        assert len(sentences) > 0
        
        # Create registry and controller
        registry = AnalyzerRegistry()
        from src.langquality.config.models import PipelineConfig, AnalysisConfig
        config = PipelineConfig(
            analysis=AnalysisConfig(),
            input_directory="test",
            output_directory="test_output",
            enable_analyzers=["all"]
        )
        controller = PipelineController(config, pack, registry)
        
        # Run pipeline
        results = controller.run(sentences)
        
        # Verify results
        assert results is not None
        assert results.structural is not None
        assert results.structural.total_sentences == len(sentences)
    
    def test_pipeline_with_minimal_pack(self, pack_manager, temp_output_dir):
        """Test pipeline execution with minimal language pack."""
        # Load minimal pack
        pack = pack_manager.load_language_pack("test_minimal")
        
        # Load data
        dataset_path = get_test_dataset_path("test_english.csv")
        loader = GenericDataLoader(pack)
        sentences = loader.load_from_csv(str(dataset_path))
        
        # Create registry and controller
        registry = AnalyzerRegistry()
        from src.langquality.config.models import PipelineConfig, AnalysisConfig
        config = PipelineConfig(
            analysis=AnalysisConfig(),
            input_directory="test",
            output_directory="test_output",
            enable_analyzers=["all"]
        )
        controller = PipelineController(config, pack, registry)
        
        # Run pipeline - should work with limited functionality
        results = controller.run(sentences)
        
        assert results is not None
        # At least structural analysis should work
        assert results.structural is not None
    
    def test_pipeline_with_different_datasets(self, pack_manager):
        """Test pipeline with different language datasets."""
        pack = pack_manager.load_language_pack("test_complete")
        registry = AnalyzerRegistry()
        from src.langquality.config.models import PipelineConfig, AnalysisConfig
        config = PipelineConfig(
            analysis=AnalysisConfig(),
            input_directory="test",
            output_directory="test_output",
            enable_analyzers=["all"]
        )
        controller = PipelineController(config, pack, registry)
        
        datasets = ["test_english.csv", "test_french.csv", "test_fongbe.csv"]
        
        for dataset_name in datasets:
            dataset_path = get_test_dataset_path(dataset_name)
            loader = GenericDataLoader(pack)
            sentences = loader.load_from_csv(str(dataset_path))
            
            results = controller.run(sentences)
            
            assert results is not None
            assert results.structural is not None
            assert results.structural.total_sentences == len(sentences)


class TestMultiLanguagePipeline:
    """Tests for pipeline with multiple language packs."""
    
    @pytest.fixture
    def pack_manager(self):
        """Create language pack manager."""
        return LanguagePackManager(get_language_packs_dir())
    
    def test_switch_between_language_packs(self, pack_manager):
        """Test switching between different language packs."""
        registry = AnalyzerRegistry()
        
        # Test with complete pack
        pack1 = pack_manager.load_language_pack("test_complete")
        from src.langquality.config.models import PipelineConfig, AnalysisConfig
        config = PipelineConfig(
            analysis=AnalysisConfig(),
            input_directory="test",
            output_directory="test_output",
            enable_analyzers=["all"]
        )
        controller1 = PipelineController(config, pack1, registry)
        
        dataset1 = get_test_dataset_path("test_english.csv")
        loader1 = GenericDataLoader(pack1)
        sentences1 = loader1.load_from_csv(str(dataset1))
        results1 = controller1.run(sentences1)
        
        assert results1 is not None
        
        # Test with minimal pack
        pack2 = pack_manager.load_language_pack("test_minimal")
        controller2 = PipelineController(pack2, registry)
        
        dataset2 = get_test_dataset_path("test_french.csv")
        loader2 = GenericDataLoader(pack2)
        sentences2 = loader2.load_from_csv(str(dataset2))
        results2 = controller2.run(sentences2)
        
        assert results2 is not None
        
        # Results should be independent
        assert results1 is not results2
    
    def test_parallel_analysis_different_packs(self, pack_manager):
        """Test analyzing different datasets with different packs."""
        registry = AnalyzerRegistry()
        
        packs = {
            "test_complete": "test_english.csv",
            "test_minimal": "test_french.csv",
        }
        
        results_list = []
        
        for pack_name, dataset_name in packs.items():
            pack = pack_manager.load_language_pack(pack_name)
            from src.langquality.config.models import PipelineConfig, AnalysisConfig
            config = PipelineConfig(
                analysis=AnalysisConfig(),
                input_directory="test",
                output_directory="test_output",
                enable_analyzers=["all"]
            )
            controller = PipelineController(config, pack, registry)
            
            dataset_path = get_test_dataset_path(dataset_name)
            loader = GenericDataLoader(pack)
            sentences = loader.load_from_csv(str(dataset_path))
            
            results = controller.run(sentences)
            results_list.append(results)
        
        # All should succeed
        assert all(r is not None for r in results_list)
        assert all(r.structural is not None for r in results_list)


class TestPluginSystemIntegration:
    """Integration tests for plugin system with pipeline."""
    
    @pytest.fixture
    def pack_manager(self):
        """Create language pack manager."""
        return LanguagePackManager(get_language_packs_dir())
    
    def test_pipeline_with_custom_plugins(self, pack_manager):
        """Test pipeline with custom analyzer plugins."""
        pack = pack_manager.load_language_pack("test_complete")
        
        # Create registry and load plugins
        registry = AnalyzerRegistry()
        plugin_dir = get_test_plugin_dir()
        loaded_count = registry.discover_plugins(str(plugin_dir))
        
        assert loaded_count >= 2
        assert registry.has_analyzer("test_custom")
        
        # Load data
        dataset_path = get_test_dataset_path("test_english.csv")
        loader = GenericDataLoader(pack)
        sentences = loader.load_from_csv(str(dataset_path))
        
        # Get custom analyzer and run it
        custom_analyzer_class = registry.get_analyzer("test_custom")
        custom_analyzer = custom_analyzer_class(language_pack=pack)
        
        metrics = custom_analyzer.analyze(sentences)
        
        assert metrics is not None
        assert metrics.total_sentences == len(sentences)
        assert metrics.custom_score >= 0
    
    def test_pipeline_with_resource_dependent_plugin(self, pack_manager):
        """Test pipeline with resource-dependent plugin."""
        pack = pack_manager.load_language_pack("test_complete")
        
        # Create registry and load plugins
        registry = AnalyzerRegistry()
        plugin_dir = get_test_plugin_dir()
        registry.discover_plugins(str(plugin_dir))
        
        # Get resource analyzer
        resource_analyzer_class = registry.get_analyzer("test_resource")
        resource_analyzer = resource_analyzer_class(language_pack=pack)
        
        # Check it can run with complete pack
        can_run, reason = resource_analyzer.can_run()
        assert can_run is True
        
        # Load data and analyze
        dataset_path = get_test_dataset_path("test_english.csv")
        loader = GenericDataLoader(pack)
        sentences = loader.load_from_csv(str(dataset_path))
        
        metrics = resource_analyzer.analyze(sentences)
        
        assert metrics is not None
        assert metrics.has_lexicon is True
        assert metrics.lexicon_matches >= 0
    
    def test_plugin_graceful_degradation(self, pack_manager):
        """Test plugin graceful degradation with minimal pack."""
        pack = pack_manager.load_language_pack("test_minimal")
        
        # Create registry and load plugins
        registry = AnalyzerRegistry()
        plugin_dir = get_test_plugin_dir()
        registry.discover_plugins(str(plugin_dir))
        
        # Resource analyzer should report it can't run
        resource_analyzer_class = registry.get_analyzer("test_resource")
        resource_analyzer = resource_analyzer_class(language_pack=pack)
        
        can_run, reason = resource_analyzer.can_run()
        assert can_run is False
        assert "lexicon" in reason.lower()


class TestGracefulDegradation:
    """Tests for graceful degradation with missing resources."""
    
    @pytest.fixture
    def pack_manager(self):
        """Create language pack manager."""
        return LanguagePackManager(get_language_packs_dir())
    
    def test_pipeline_disables_analyzers_without_resources(self, pack_manager):
        """Test that pipeline disables analyzers without required resources."""
        pack = pack_manager.load_language_pack("test_minimal")
        registry = AnalyzerRegistry()
        from src.langquality.config.models import PipelineConfig, AnalysisConfig
        config = PipelineConfig(
            analysis=AnalysisConfig(),
            input_directory="test",
            output_directory="test_output",
            enable_analyzers=["all"]
        )
        controller = PipelineController(config, pack, registry)
        
        # Load data
        dataset_path = get_test_dataset_path("test_english.csv")
        loader = GenericDataLoader(pack)
        sentences = loader.load_from_csv(str(dataset_path))
        
        # Run pipeline
        results = controller.run(sentences)
        
        # Should complete without errors
        assert results is not None
        
        # Structural should work (no resource requirements)
        assert results.structural is not None
        
        # Others may be None if they require resources
        # This is expected graceful degradation
    
    def test_pipeline_continues_on_analyzer_failure(self, pack_manager):
        """Test that pipeline continues if one analyzer fails."""
        pack = pack_manager.load_language_pack("test_complete")
        registry = AnalyzerRegistry()
        
        # Create a failing analyzer
        from src.langquality.analyzers.base import Analyzer
        from src.langquality.data.models import Sentence
        from typing import List
        
        class FailingAnalyzer(Analyzer):
            def analyze(self, sentences: List[Sentence]):
                raise RuntimeError("Intentional failure")
            
            def get_requirements(self):
                return []
            
            def can_run(self):
                return True, None
            
            @property
            def name(self):
                return "failing"
            
            @property
            def version(self):
                return "1.0.0"
        
        # Register failing analyzer
        registry.register("failing", FailingAnalyzer)
        
        # Load data
        dataset_path = get_test_dataset_path("test_english.csv")
        loader = GenericDataLoader(pack)
        sentences = loader.load_from_csv(str(dataset_path))
        
        # Pipeline should handle the failure gracefully
        from src.langquality.config.models import PipelineConfig, AnalysisConfig
        config = PipelineConfig(
            analysis=AnalysisConfig(),
            input_directory="test",
            output_directory="test_output",
            enable_analyzers=["all"]
        )
        controller = PipelineController(config, pack, registry)
        
        try:
            results = controller.run(sentences)
            # If it completes, other analyzers should have run
            assert results is not None
        except Exception as e:
            # Or it should raise a clear error
            assert "failing" in str(e).lower() or "error" in str(e).lower()


class TestDataLoaderIntegration:
    """Integration tests for data loader with language packs."""
    
    @pytest.fixture
    def pack_manager(self):
        """Create language pack manager."""
        return LanguagePackManager(get_language_packs_dir())
    
    def test_load_csv_with_language_pack(self, pack_manager):
        """Test loading CSV with language pack."""
        pack = pack_manager.load_language_pack("test_complete")
        loader = GenericDataLoader(pack)
        
        dataset_path = get_test_dataset_path("test_english.csv")
        sentences = loader.load_from_csv(str(dataset_path))
        
        assert len(sentences) > 0
        assert all(hasattr(s, 'text') for s in sentences)
        assert all(hasattr(s, 'word_count') for s in sentences)
    
    def test_tokenization_with_language_pack(self, pack_manager):
        """Test that tokenization uses language pack configuration."""
        pack = pack_manager.load_language_pack("test_complete")
        loader = GenericDataLoader(pack)
        
        # Pack uses whitespace tokenization
        assert pack.config.tokenization.method == "whitespace"
        
        dataset_path = get_test_dataset_path("test_english.csv")
        sentences = loader.load_from_csv(str(dataset_path))
        
        # Verify tokenization was applied
        for sentence in sentences:
            assert sentence.word_count > 0
            # Word count should match whitespace-split count
            expected_count = len(sentence.text.split())
            assert sentence.word_count == expected_count
    
    def test_load_multiple_formats(self, pack_manager):
        """Test loading different file formats with language pack."""
        pack = pack_manager.load_language_pack("test_complete")
        loader = GenericDataLoader(pack)
        
        # Test CSV
        csv_path = get_test_dataset_path("test_english.csv")
        csv_sentences = loader.load_from_csv(str(csv_path))
        assert len(csv_sentences) > 0
        
        # All formats should work with the same language pack
        assert all(isinstance(s.text, str) for s in csv_sentences)


class TestEndToEndWorkflow:
    """End-to-end workflow tests."""
    
    @pytest.fixture
    def pack_manager(self):
        """Create language pack manager."""
        return LanguagePackManager(get_language_packs_dir())
    
    def test_complete_workflow(self, pack_manager):
        """Test complete workflow from pack loading to analysis."""
        # Step 1: Load language pack
        pack = pack_manager.load_language_pack("test_complete")
        assert pack is not None
        
        # Step 2: Create analyzer registry
        registry = AnalyzerRegistry()
        assert len(registry.list_analyzers()) > 0
        
        # Step 3: Load plugins
        plugin_dir = get_test_plugin_dir()
        loaded = registry.discover_plugins(str(plugin_dir))
        assert loaded >= 2
        
        # Step 4: Load data
        dataset_path = get_test_dataset_path("test_english.csv")
        loader = GenericDataLoader(pack)
        sentences = loader.load_from_csv(str(dataset_path))
        assert len(sentences) > 0
        
        # Step 5: Create pipeline controller
        from src.langquality.config.models import PipelineConfig, AnalysisConfig
        config = PipelineConfig(
            analysis=AnalysisConfig(),
            input_directory="test",
            output_directory="test_output",
            enable_analyzers=["all"]
        )
        controller = PipelineController(config, pack, registry)
        
        # Step 6: Run analysis
        results = controller.run(sentences)
        assert results is not None
        
        # Step 7: Verify results
        assert results.structural is not None
        assert results.structural.total_sentences == len(sentences)
    
    def test_workflow_with_multiple_languages(self, pack_manager):
        """Test workflow with multiple language datasets."""
        datasets = {
            "test_english.csv": "test_complete",
            "test_french.csv": "test_complete",
            "test_fongbe.csv": "test_minimal",
        }
        
        registry = AnalyzerRegistry()
        all_results = []
        
        for dataset_name, pack_name in datasets.items():
            # Load pack
            pack = pack_manager.load_language_pack(pack_name)
            
            # Load data
            dataset_path = get_test_dataset_path(dataset_name)
            loader = GenericDataLoader(pack)
            sentences = loader.load_from_csv(str(dataset_path))
            
            # Analyze
            from src.langquality.config.models import PipelineConfig, AnalysisConfig
            config = PipelineConfig(
                analysis=AnalysisConfig(),
                input_directory="test",
                output_directory="test_output",
                enable_analyzers=["all"]
            )
            controller = PipelineController(config, pack, registry)
            results = controller.run(sentences)
            
            all_results.append({
                'dataset': dataset_name,
                'pack': pack_name,
                'results': results
            })
        
        # All should succeed
        assert len(all_results) == 3
        assert all(r['results'] is not None for r in all_results)
        assert all(r['results'].structural is not None for r in all_results)
