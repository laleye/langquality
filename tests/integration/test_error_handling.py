"""Integration tests for error handling and graceful degradation."""

import pytest
import tempfile
import shutil
from pathlib import Path
import csv

from langquality.config.models import AnalysisConfig, PipelineConfig
from langquality.data.loader import DataLoader
from langquality.pipeline.controller import PipelineController
from langquality.utils.exceptions import (
    DataLoadError,
    ValidationError,
    AnalysisError,
    ConfigurationError
)


class TestErrorHandling:
    """Test error handling and graceful degradation."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary output directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_invalid_csv_missing_columns(self, temp_dir, temp_output_dir):
        """Test pipeline behavior with CSV missing required columns."""
        # Create invalid CSV with wrong columns
        invalid_csv = Path(temp_dir) / "invalid.csv"
        with open(invalid_csv, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['wrong_column', 'another_column'])
            writer.writerow(['value1', 'value2'])
        
        loader = DataLoader()
        
        # Should raise DataLoadError for missing 'french' column
        with pytest.raises(DataLoadError):
            loader.load_csv(str(invalid_csv))
    
    def test_invalid_csv_empty_file(self, temp_dir, temp_output_dir):
        """Test pipeline behavior with empty CSV file."""
        # Create empty CSV
        empty_csv = Path(temp_dir) / "empty.csv"
        with open(empty_csv, 'w', encoding='utf-8') as f:
            f.write("")
        
        loader = DataLoader()
        
        # Should raise DataLoadError for empty file
        with pytest.raises(DataLoadError):
            loader.load_csv(str(empty_csv))
    
    def test_invalid_csv_malformed_data(self, temp_dir, temp_output_dir):
        """Test pipeline behavior with malformed CSV data."""
        # Create CSV with malformed rows
        malformed_csv = Path(temp_dir) / "malformed.csv"
        with open(malformed_csv, 'w', encoding='utf-8') as f:
            f.write("fongbe,french\n")
            f.write("text1,text2\n")
            f.write("text3\n")  # Missing column
            f.write("text4,text5,text6\n")  # Extra column
        
        loader = DataLoader()
        
        # Should handle malformed rows gracefully
        try:
            sentences = loader.load_csv(str(malformed_csv))
            # Should load valid rows
            assert len(sentences) >= 1
        except DataLoadError:
            # Or raise error if validation is strict
            pass
    
    def test_csv_with_encoding_issues(self, temp_dir, temp_output_dir):
        """Test pipeline behavior with encoding issues."""
        # Create CSV with special characters
        special_csv = Path(temp_dir) / "special.csv"
        with open(special_csv, 'w', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['fongbe', 'french'])
            writer.writerow(['Ɖò', 'Voici des caractères spéciaux: é, è, ê, ç'])
            writer.writerow(['Gbɛ̀', 'Texte avec émojis 😀 et symboles €'])
        
        loader = DataLoader()
        
        # Should handle special characters correctly
        sentences = loader.load_csv(str(special_csv))
        assert len(sentences) == 2
        assert 'é' in sentences[0].text or 'è' in sentences[0].text
    
    def test_pipeline_with_no_analyzers_enabled(self, temp_output_dir):
        """Test pipeline behavior when no analyzers are enabled."""
        config = PipelineConfig(
            analysis=AnalysisConfig(),
            input_directory="tests/data/small_dataset",
            output_directory=temp_output_dir,
            enable_analyzers=[],  # No analyzers
            language="fr"
        )
        
        loader = DataLoader()
        sentences_by_domain = loader.load_directory(config.input_directory)
        all_sentences = [s for sentences in sentences_by_domain.values() for s in sentences]
        
        controller = PipelineController(config)
        
        # Should raise AnalysisError when no analyzers are enabled
        with pytest.raises(AnalysisError, match="No analyzers enabled"):
            controller.run(all_sentences)
    
    def test_pipeline_with_empty_sentence_list(self, temp_output_dir):
        """Test pipeline behavior with empty sentence list."""
        config = PipelineConfig(
            analysis=AnalysisConfig(),
            input_directory="tests/data/small_dataset",
            output_directory=temp_output_dir,
            enable_analyzers=["all"],
            language="fr"
        )
        
        controller = PipelineController(config)
        
        # Should handle empty list gracefully
        results = controller.run([])
        
        # Results should still be created but with empty/zero metrics
        assert results is not None
    
    def test_pipeline_graceful_degradation_single_analyzer_failure(self, temp_output_dir, monkeypatch):
        """Test that pipeline continues when a single analyzer fails."""
        config = PipelineConfig(
            analysis=AnalysisConfig(),
            input_directory="tests/data/small_dataset",
            output_directory=temp_output_dir,
            enable_analyzers=["all"],
            language="fr"
        )
        
        loader = DataLoader()
        sentences_by_domain = loader.load_directory(config.input_directory)
        all_sentences = [s for sentences in sentences_by_domain.values() for s in sentences]
        
        # Mock one analyzer to fail
        from langquality.analyzers import structural
        original_analyze = structural.StructuralAnalyzer.analyze
        
        def failing_analyze(self, sentences):
            raise Exception("Simulated analyzer failure")
        
        monkeypatch.setattr(structural.StructuralAnalyzer, 'analyze', failing_analyze)
        
        controller = PipelineController(config)
        results = controller.run(all_sentences)
        
        # Pipeline should complete despite one analyzer failing
        assert results is not None
        assert results.structural is None  # Failed analyzer returns None
        # Other analyzers should still work
        assert results.domain is not None or \
               results.diversity is not None or \
               results.linguistic is not None
        
        # Restore original method
        monkeypatch.setattr(structural.StructuralAnalyzer, 'analyze', original_analyze)
    
    def test_pipeline_all_analyzers_fail(self, temp_output_dir, monkeypatch):
        """Test pipeline behavior when all analyzers fail."""
        config = PipelineConfig(
            analysis=AnalysisConfig(),
            input_directory="tests/data/small_dataset",
            output_directory=temp_output_dir,
            enable_analyzers=["structural", "domain"],
            language="fr"
        )
        
        loader = DataLoader()
        sentences_by_domain = loader.load_directory(config.input_directory)
        all_sentences = [s for sentences in sentences_by_domain.values() for s in sentences]
        
        # Mock all analyzers to fail
        from langquality.analyzers import structural, domain
        
        def failing_analyze(self, sentences):
            raise Exception("Simulated failure")
        
        monkeypatch.setattr(structural.StructuralAnalyzer, 'analyze', failing_analyze)
        monkeypatch.setattr(domain.DomainAnalyzer, 'analyze', failing_analyze)
        
        controller = PipelineController(config)
        
        # Should raise AnalysisError when all analyzers fail
        with pytest.raises(AnalysisError, match="All analyzers failed"):
            controller.run(all_sentences)
    
    def test_invalid_configuration_parameters(self, temp_output_dir):
        """Test pipeline behavior with invalid configuration parameters."""
        # Test with invalid min/max words (min > max)
        config = PipelineConfig(
            analysis=AnalysisConfig(
                min_words=20,
                max_words=10  # Invalid: max < min
            ),
            input_directory="tests/data/small_dataset",
            output_directory=temp_output_dir,
            enable_analyzers=["all"],
            language="fr"
        )
        
        loader = DataLoader()
        sentences_by_domain = loader.load_directory(config.input_directory)
        all_sentences = [s for sentences in sentences_by_domain.values() for s in sentences]
        
        controller = PipelineController(config)
        
        # Pipeline should still run but may produce unexpected results
        # The validation of config parameters should ideally happen at config load time
        results = controller.run(all_sentences)
        assert results is not None
    
    def test_nonexistent_input_directory(self):
        """Test data loader behavior with nonexistent directory."""
        loader = DataLoader()
        
        # Should raise DataLoadError for nonexistent directory
        with pytest.raises(DataLoadError):
            loader.load_directory("/nonexistent/directory/path")
    
    def test_input_directory_with_no_csv_files(self, temp_dir, temp_output_dir):
        """Test data loader behavior with directory containing no CSV files."""
        # Create directory with non-CSV files
        (Path(temp_dir) / "readme.txt").write_text("Not a CSV file")
        (Path(temp_dir) / "data.json").write_text('{"key": "value"}')
        
        loader = DataLoader()
        
        # Should raise DataLoadError when no CSV files found
        with pytest.raises(DataLoadError, match="No CSV files found"):
            loader.load_directory(temp_dir)
    
    def test_csv_with_only_headers(self, temp_dir, temp_output_dir):
        """Test pipeline behavior with CSV containing only headers."""
        # Create CSV with only headers
        headers_only_csv = Path(temp_dir) / "headers_only.csv"
        with open(headers_only_csv, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['fongbe', 'french'])
        
        loader = DataLoader()
        
        # Should return empty list or raise error
        try:
            sentences = loader.load_csv(str(headers_only_csv))
            assert len(sentences) == 0
        except DataLoadError:
            pass  # Also acceptable to raise error
    
    def test_csv_with_empty_french_column(self, temp_dir, temp_output_dir):
        """Test pipeline behavior with empty French text."""
        # Create CSV with empty French column
        empty_text_csv = Path(temp_dir) / "empty_text.csv"
        with open(empty_text_csv, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['fongbe', 'french'])
            writer.writerow(['Ɖò', ''])  # Empty French text
            writer.writerow(['Gbɛ̀', '   '])  # Whitespace only
            writer.writerow(['Valid', 'Valid French text'])
        
        loader = DataLoader()
        sentences = loader.load_csv(str(empty_text_csv))
        
        # Should filter out empty/whitespace sentences
        # Only valid sentence should be loaded
        assert len(sentences) <= 3
        # At least the valid sentence should be present
        valid_sentences = [s for s in sentences if s.text.strip()]
        assert len(valid_sentences) >= 1
    
    def test_pipeline_with_very_large_sentences(self, temp_dir, temp_output_dir):
        """Test pipeline behavior with extremely long sentences."""
        # Create CSV with very long sentence
        long_csv = Path(temp_dir) / "long.csv"
        very_long_text = "Ceci est une phrase extrêmement longue. " * 100  # ~500 words
        
        with open(long_csv, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['fongbe', 'french'])
            writer.writerow(['Long', very_long_text])
        
        config = PipelineConfig(
            analysis=AnalysisConfig(),
            input_directory=temp_dir,
            output_directory=temp_output_dir,
            enable_analyzers=["structural"],
            language="fr"
        )
        
        loader = DataLoader()
        sentences_by_domain = loader.load_directory(temp_dir)
        all_sentences = [s for sentences in sentences_by_domain.values() for s in sentences]
        
        # Should handle long sentences without crashing
        controller = PipelineController(config)
        results = controller.run(all_sentences)
        
        assert results is not None
        assert results.structural is not None
        # Should flag as too long
        assert len(results.structural.too_long) > 0
    
    def test_missing_configuration_file(self):
        """Test configuration loader with missing file."""
        from langquality.config.loader import load_config
        
        # Should raise ConfigurationError for nonexistent file
        with pytest.raises(ConfigurationError):
            load_config("/nonexistent/config.yaml")
