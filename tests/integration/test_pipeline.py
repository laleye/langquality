"""Integration tests for end-to-end pipeline execution."""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from langquality.config.models import AnalysisConfig, PipelineConfig
from langquality.data.loader import DataLoader
from langquality.pipeline.controller import PipelineController
from langquality.recommendations.engine import RecommendationEngine
from langquality.recommendations.best_practices import BestPractices
from langquality.outputs.exporters import ExportManager
from langquality.outputs.dashboard import DashboardGenerator


class TestEndToEndPipeline:
    """Test complete pipeline execution with real data."""
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary output directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def default_config(self, temp_output_dir):
        """Create a default pipeline configuration."""
        analysis_config = AnalysisConfig(
            min_words=3,
            max_words=20,
            max_readability_score=60.0,
            target_ttr=0.6,
            min_domain_representation=0.10,
            max_domain_representation=0.30
        )
        
        return PipelineConfig(
            analysis=analysis_config,
            input_directory="tests/data/small_dataset",
            output_directory=temp_output_dir,
            enable_analyzers=["all"],
            language="fr"
        )
    
    def test_complete_pipeline_execution(self, default_config):
        """Test complete pipeline execution from data loading to results."""
        # Step 1: Load data
        loader = DataLoader()
        sentences_by_domain = loader.load_directory(default_config.input_directory)
        
        # Flatten sentences
        all_sentences = []
        for domain_sentences in sentences_by_domain.values():
            all_sentences.extend(domain_sentences)
        
        assert len(all_sentences) > 0, "Should load sentences from test data"
        
        # Step 2: Run pipeline
        controller = PipelineController(default_config)
        results = controller.run(all_sentences)
        
        # Verify results structure
        assert results is not None
        assert results.timestamp is not None
        assert isinstance(results.timestamp, datetime)
        assert results.config_used == default_config
        
        # Verify at least some analyzers ran successfully
        assert results.structural is not None or \
               results.linguistic is not None or \
               results.diversity is not None or \
               results.domain is not None or \
               results.gender_bias is not None
        
        # Step 3: Generate recommendations
        rec_engine = RecommendationEngine(BestPractices())
        recommendations = rec_engine.generate_recommendations(results)
        
        assert isinstance(recommendations, list)
        # Recommendations may be empty if data quality is perfect
        
        # Step 4: Verify outputs can be generated
        exporter = ExportManager()
        output_path = Path(default_config.output_directory)
        
        # Test JSON export
        json_path = output_path / "test_results.json"
        exporter.export_json(results, str(json_path))
        assert json_path.exists()
        
        # Test execution log
        log_path = output_path / "test_log.txt"
        exporter.create_execution_log(results, str(log_path))
        assert log_path.exists()
        
        # Test dashboard generation
        dashboard_gen = DashboardGenerator()
        dashboard_html = dashboard_gen.generate(results, recommendations)
        assert isinstance(dashboard_html, str)
        assert len(dashboard_html) > 0
        assert "<html" in dashboard_html.lower()
    
    def test_pipeline_with_all_outputs(self, default_config):
        """Test pipeline generates all expected output files."""
        # Load and analyze data
        loader = DataLoader()
        sentences_by_domain = loader.load_directory(default_config.input_directory)
        all_sentences = [s for sentences in sentences_by_domain.values() for s in sentences]
        
        controller = PipelineController(default_config)
        results = controller.run(all_sentences)
        
        rec_engine = RecommendationEngine(BestPractices())
        recommendations = rec_engine.generate_recommendations(results)
        
        # Generate all outputs
        exporter = ExportManager()
        output_path = Path(default_config.output_directory)
        
        # JSON export
        json_path = output_path / "results.json"
        exporter.export_json(results, str(json_path))
        
        # Annotated CSV
        csv_path = output_path / "annotated.csv"
        scores = {'min_words': default_config.analysis.min_words}
        exporter.export_annotated_csv(all_sentences, scores, str(csv_path))
        
        # Filtered sentences
        filtered_path = output_path / "filtered.csv"
        rejected = []
        if results.structural:
            for sentence in results.structural.too_short[:5]:  # Limit for test
                rejected.append({
                    'sentence': sentence,
                    'reason': 'too_short',
                    'details': f'Only {sentence.word_count} words'
                })
        if rejected:
            exporter.export_filtered_sentences(rejected, str(filtered_path))
        
        # Execution log
        log_path = output_path / "log.txt"
        exporter.create_execution_log(results, str(log_path))
        
        # PDF report
        pdf_path = output_path / "report.pdf"
        exporter.export_pdf_report(results, recommendations, str(pdf_path))
        
        # Dashboard
        dashboard_path = output_path / "dashboard.html"
        dashboard_gen = DashboardGenerator()
        dashboard_html = dashboard_gen.generate(results, recommendations)
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(dashboard_html)
        
        # Verify all files exist
        assert json_path.exists()
        assert csv_path.exists()
        assert log_path.exists()
        assert pdf_path.exists()
        assert dashboard_path.exists()
    
    def test_pipeline_with_different_configurations(self, temp_output_dir):
        """Test pipeline with various configuration settings."""
        # Test with only structural analyzer
        config1 = PipelineConfig(
            analysis=AnalysisConfig(),
            input_directory="tests/data/small_dataset",
            output_directory=temp_output_dir,
            enable_analyzers=["structural"],
            language="fr"
        )
        
        loader = DataLoader()
        sentences_by_domain = loader.load_directory(config1.input_directory)
        all_sentences = [s for sentences in sentences_by_domain.values() for s in sentences]
        
        controller1 = PipelineController(config1)
        results1 = controller1.run(all_sentences)
        
        assert results1.structural is not None
        # Other analyzers should be None since not enabled
        
        # Test with multiple specific analyzers
        config2 = PipelineConfig(
            analysis=AnalysisConfig(),
            input_directory="tests/data/small_dataset",
            output_directory=temp_output_dir,
            enable_analyzers=["structural", "domain", "diversity"],
            language="fr"
        )
        
        controller2 = PipelineController(config2)
        results2 = controller2.run(all_sentences)
        
        assert results2.structural is not None
        assert results2.domain is not None
        assert results2.diversity is not None
        
        # Test with custom thresholds
        config3 = PipelineConfig(
            analysis=AnalysisConfig(
                min_words=5,
                max_words=15,
                max_readability_score=50.0
            ),
            input_directory="tests/data/small_dataset",
            output_directory=temp_output_dir,
            enable_analyzers=["all"],
            language="fr"
        )
        
        controller3 = PipelineController(config3)
        results3 = controller3.run(all_sentences)
        
        # Verify custom thresholds were applied
        assert results3.config_used.analysis.min_words == 5
        assert results3.config_used.analysis.max_words == 15
    
    def test_pipeline_with_edge_cases_dataset(self, temp_output_dir):
        """Test pipeline with edge cases dataset."""
        config = PipelineConfig(
            analysis=AnalysisConfig(),
            input_directory="tests/data/edge_cases",
            output_directory=temp_output_dir,
            enable_analyzers=["all"],
            language="fr"
        )
        
        loader = DataLoader()
        sentences_by_domain = loader.load_directory(config.input_directory)
        all_sentences = [s for sentences in sentences_by_domain.values() for s in sentences]
        
        # Should handle edge cases without crashing
        controller = PipelineController(config)
        results = controller.run(all_sentences)
        
        assert results is not None
        # Edge cases should trigger quality issues
        if results.structural:
            assert len(results.structural.too_short) > 0 or len(results.structural.too_long) > 0
    
    def test_pipeline_metrics_consistency(self, default_config):
        """Test that pipeline metrics are consistent and valid."""
        loader = DataLoader()
        sentences_by_domain = loader.load_directory(default_config.input_directory)
        all_sentences = [s for sentences in sentences_by_domain.values() for s in sentences]
        
        controller = PipelineController(default_config)
        results = controller.run(all_sentences)
        
        # Verify structural metrics
        if results.structural:
            assert results.structural.total_sentences == len(all_sentences)
            assert results.structural.word_distribution['mean'] > 0
            assert results.structural.word_distribution['min'] >= 0
            assert results.structural.word_distribution['max'] >= results.structural.word_distribution['min']
        
        # Verify diversity metrics
        if results.diversity:
            assert 0 <= results.diversity.ttr <= 1.0
            assert results.diversity.unique_words <= results.diversity.total_words
            assert results.diversity.total_words > 0
        
        # Verify domain metrics
        if results.domain:
            assert results.domain.total_domains > 0
            total_percentage = sum(results.domain.domain_percentages.values())
            assert 0.99 <= total_percentage <= 1.01  # Allow for rounding
        
        # Verify gender bias metrics
        if results.gender_bias:
            assert results.gender_bias.gender_ratio >= 0
            assert results.gender_bias.bias_score >= 0
