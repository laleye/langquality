"""Unit tests for export functionality."""

import json
import csv
import tempfile
from pathlib import Path
from datetime import datetime

from langquality.outputs.exporters import ExportManager
from langquality.pipeline.results import AnalysisResults
from langquality.data.models import Sentence
from langquality.config.models import AnalysisConfig, PipelineConfig
from langquality.analyzers.structural import StructuralMetrics
from langquality.recommendations.models import Recommendation


def test_export_json():
    """Test JSON export functionality."""
    # Create sample data
    config = PipelineConfig(
        analysis=AnalysisConfig(),
        input_directory="test",
        output_directory="test_output",
        language="fr"
    )
    
    structural = StructuralMetrics(
        total_sentences=10,
        char_distribution={"mean": 50.0, "median": 48.0, "std": 10.0},
        word_distribution={"mean": 10.0, "median": 9.0, "std": 2.0},
        too_short=[],
        too_long=[],
        length_histogram={5: 2, 10: 5, 15: 3}
    )
    
    results = AnalysisResults(
        structural=structural,
        linguistic=None,
        diversity=None,
        domain=None,
        gender_bias=None,
        timestamp=datetime.now(),
        config_used=config
    )
    
    # Export to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name
    
    try:
        exporter = ExportManager()
        exporter.export_json(results, temp_path)
        
        # Verify file was created and contains valid JSON
        assert Path(temp_path).exists()
        
        with open(temp_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert 'metadata' in data
        assert 'structural' in data
        assert data['structural']['total_sentences'] == 10
        
    finally:
        # Cleanup
        Path(temp_path).unlink(missing_ok=True)


def test_export_annotated_csv():
    """Test annotated CSV export functionality."""
    # Create sample sentences
    sentences = [
        Sentence(
            text="Bonjour, comment allez-vous?",
            domain="greeting",
            source_file="test.csv",
            line_number=1,
            char_count=28,
            word_count=4,
            metadata={}
        ),
        Sentence(
            text="Cette phrase est très longue et contient beaucoup de mots pour tester.",
            domain="test",
            source_file="test.csv",
            line_number=2,
            char_count=72,
            word_count=12,
            metadata={}
        )
    ]
    
    scores = {
        "test.csv:1": {
            "readability_score": 65.0,
            "lexical_complexity": 0.3,
            "has_jargon": False,
            "is_complex_syntax": False
        },
        "test.csv:2": {
            "readability_score": 45.0,
            "lexical_complexity": 0.6,
            "has_jargon": True,
            "is_complex_syntax": True
        },
        "min_words": 3,
        "max_words": 20
    }
    
    # Export to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        temp_path = f.name
    
    try:
        exporter = ExportManager()
        exporter.export_annotated_csv(sentences, scores, temp_path)
        
        # Verify file was created and contains correct data
        assert Path(temp_path).exists()
        
        with open(temp_path, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        assert len(rows) == 2
        assert rows[0]['text'] == "Bonjour, comment allez-vous?"
        assert rows[0]['quality_flag'] == "pass"
        assert rows[1]['has_jargon'] == "True"
        
    finally:
        # Cleanup
        Path(temp_path).unlink(missing_ok=True)


def test_export_filtered_sentences():
    """Test filtered sentences export functionality."""
    # Create sample rejected sentences
    rejected = [
        {
            "sentence": Sentence(
                text="Hi",
                domain="test",
                source_file="test.csv",
                line_number=1,
                char_count=2,
                word_count=1,
                metadata={}
            ),
            "reason": "too_short",
            "details": "Only 1 word, minimum is 3"
        }
    ]
    
    # Export to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        temp_path = f.name
    
    try:
        exporter = ExportManager()
        exporter.export_filtered_sentences(rejected, temp_path)
        
        # Verify file was created and contains correct data
        assert Path(temp_path).exists()
        
        with open(temp_path, 'r', encoding='utf-8', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        assert len(rows) == 1
        assert rows[0]['text'] == "Hi"
        assert rows[0]['rejection_reason'] == "too_short"
        
    finally:
        # Cleanup
        Path(temp_path).unlink(missing_ok=True)


def test_create_execution_log():
    """Test execution log creation."""
    # Create sample data
    config = PipelineConfig(
        analysis=AnalysisConfig(),
        input_directory="test",
        output_directory="test_output",
        language="fr"
    )
    
    structural = StructuralMetrics(
        total_sentences=100,
        char_distribution={"mean": 50.0, "median": 48.0, "std": 10.0},
        word_distribution={"mean": 10.0, "median": 9.0, "std": 2.0},
        too_short=[],
        too_long=[],
        length_histogram={}
    )
    
    results = AnalysisResults(
        structural=structural,
        linguistic=None,
        diversity=None,
        domain=None,
        gender_bias=None,
        timestamp=datetime.now(),
        config_used=config
    )
    
    # Export to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
        temp_path = f.name
    
    try:
        exporter = ExportManager()
        exporter.create_execution_log(results, temp_path)
        
        # Verify file was created and contains expected content
        assert Path(temp_path).exists()
        
        with open(temp_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert "FONGBE DATA QUALITY ANALYSIS" in content
        assert "EXECUTION LOG" in content
        assert "Total Sentences: 100" in content
        assert "CONFIGURATION" in content
        
    finally:
        # Cleanup
        Path(temp_path).unlink(missing_ok=True)


def test_export_pdf_report():
    """Test PDF report generation."""
    # Create sample data
    config = PipelineConfig(
        analysis=AnalysisConfig(),
        input_directory="test",
        output_directory="test_output",
        language="fr"
    )
    
    structural = StructuralMetrics(
        total_sentences=50,
        char_distribution={"mean": 45.0, "median": 44.0, "std": 8.0},
        word_distribution={"mean": 9.0, "median": 8.0, "std": 2.0},
        too_short=[],
        too_long=[],
        length_histogram={5: 10, 10: 30, 15: 10}
    )
    
    results = AnalysisResults(
        structural=structural,
        linguistic=None,
        diversity=None,
        domain=None,
        gender_bias=None,
        timestamp=datetime.now(),
        config_used=config
    )
    
    recommendations = [
        Recommendation(
            category="structural",
            severity="warning",
            title="Test recommendation",
            description="This is a test recommendation",
            affected_items=[],
            suggested_actions=["Action 1", "Action 2"],
            priority=2
        )
    ]
    
    # Export to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
        temp_path = f.name
    
    try:
        exporter = ExportManager()
        exporter.export_pdf_report(results, recommendations, temp_path)
        
        # Verify file was created
        assert Path(temp_path).exists()
        
        # Verify it's a PDF file (check magic bytes)
        with open(temp_path, 'rb') as f:
            header = f.read(4)
            assert header == b'%PDF'
        
    finally:
        # Cleanup
        Path(temp_path).unlink(missing_ok=True)
