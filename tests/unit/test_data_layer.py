"""Unit tests for data layer (loader, validator, models)."""

import tempfile
import csv
from pathlib import Path

from src.langquality.data.loader import DataLoader
from src.langquality.data.validator import DataValidator
from src.langquality.data.models import Sentence, ValidationResult
from src.langquality.utils.exceptions import DataLoadError
import pytest


class TestDataLoader:
    """Tests for DataLoader class."""
    
    def test_load_csv_basic(self):
        """Test loading a basic CSV file."""
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            temp_path = f.name
            writer = csv.writer(f)
            writer.writerow(['text'])
            writer.writerow(['Bonjour, comment allez-vous?'])
            writer.writerow(['Cette phrase est un test.'])
        
        try:
            loader = DataLoader()
            sentences = loader.load_csv(temp_path)
            
            assert len(sentences) == 2
            assert sentences[0].text == 'Bonjour, comment allez-vous?'
            assert sentences[0].word_count == 4
            assert sentences[0].char_count == 28
            assert sentences[1].text == 'Cette phrase est un test.'
            
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    def test_load_csv_without_header(self):
        """Test loading CSV without header."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            temp_path = f.name
            writer = csv.writer(f)
            writer.writerow(['Première phrase sans en-tête.'])
            writer.writerow(['Deuxième phrase.'])
        
        try:
            loader = DataLoader()
            sentences = loader.load_csv(temp_path)
            
            assert len(sentences) == 2
            assert sentences[0].text == 'Première phrase sans en-tête.'
            
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    def test_load_csv_skip_empty_rows(self):
        """Test that empty rows are skipped."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            temp_path = f.name
            writer = csv.writer(f)
            writer.writerow(['text'])
            writer.writerow(['Phrase valide.'])
            writer.writerow([''])  # Empty row
            writer.writerow(['   '])  # Whitespace only
            writer.writerow(['Autre phrase valide.'])
        
        try:
            loader = DataLoader()
            sentences = loader.load_csv(temp_path)
            
            assert len(sentences) == 2
            assert sentences[0].text == 'Phrase valide.'
            assert sentences[1].text == 'Autre phrase valide.'
            
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    def test_load_csv_file_not_found(self):
        """Test error handling for non-existent file."""
        loader = DataLoader()
        
        with pytest.raises(DataLoadError, match="File not found"):
            loader.load_csv("nonexistent_file.csv")
    
    def test_load_csv_empty_file(self):
        """Test error handling for empty CSV file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            temp_path = f.name
            # Write nothing
        
        try:
            loader = DataLoader()
            
            with pytest.raises(DataLoadError, match="No valid sentences found"):
                loader.load_csv(temp_path)
                
        finally:
            Path(temp_path).unlink(missing_ok=True)
    
    def test_extract_domain_from_filename(self):
        """Test domain extraction from filename."""
        loader = DataLoader()
        
        assert loader.extract_domain_from_filename("health.csv") == "health"
        assert loader.extract_domain_from_filename("education_data.csv") == "education_data"
        assert loader.extract_domain_from_filename("commerce-sentences.csv") == "commerce-sentences"
        assert loader.extract_domain_from_filename("test.CSV") == "test"
        assert loader.extract_domain_from_filename(".csv") == "unknown"
    
    def test_load_directory(self):
        """Test loading multiple CSV files from directory."""
        # Create temporary directory with CSV files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create first CSV
            csv1_path = Path(temp_dir) / "health.csv"
            with open(csv1_path, 'w', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['text'])
                writer.writerow(['Phrase de santé.'])
            
            # Create second CSV
            csv2_path = Path(temp_dir) / "education.csv"
            with open(csv2_path, 'w', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['text'])
                writer.writerow(['Phrase d\'éducation.'])
                writer.writerow(['Autre phrase d\'éducation.'])
            
            loader = DataLoader()
            all_sentences = loader.load_directory(temp_dir)
            
            assert 'health' in all_sentences
            assert 'education' in all_sentences
            assert len(all_sentences['health']) == 1
            assert len(all_sentences['education']) == 2
    
    def test_load_directory_not_found(self):
        """Test error handling for non-existent directory."""
        loader = DataLoader()
        
        with pytest.raises(DataLoadError, match="Directory not found"):
            loader.load_directory("nonexistent_directory")
    
    def test_load_directory_no_csv_files(self):
        """Test error handling for directory with no CSV files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a non-CSV file
            txt_path = Path(temp_dir) / "test.txt"
            txt_path.write_text("Not a CSV")
            
            loader = DataLoader()
            
            with pytest.raises(DataLoadError, match="No CSV files found"):
                loader.load_directory(temp_dir)


class TestDataValidator:
    """Tests for DataValidator class."""
    
    def test_validate_sentence_valid(self):
        """Test validation of a valid sentence."""
        sentence = Sentence(
            text="Bonjour, comment allez-vous?",
            domain="greeting",
            source_file="test.csv",
            line_number=1,
            char_count=28,
            word_count=4,
            metadata={}
        )
        
        validator = DataValidator()
        result = validator.validate_sentence(sentence)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_sentence_empty_text(self):
        """Test validation of sentence with empty text."""
        sentence = Sentence(
            text="",
            domain="test",
            source_file="test.csv",
            line_number=1,
            char_count=0,
            word_count=0,
            metadata={}
        )
        
        validator = DataValidator()
        result = validator.validate_sentence(sentence)
        
        assert result.is_valid is False
        assert any("empty" in error.lower() for error in result.errors)
    
    def test_validate_sentence_whitespace_only(self):
        """Test validation of sentence with whitespace only."""
        sentence = Sentence(
            text="   ",
            domain="test",
            source_file="test.csv",
            line_number=1,
            char_count=3,
            word_count=0,
            metadata={}
        )
        
        validator = DataValidator()
        result = validator.validate_sentence(sentence)
        
        assert result.is_valid is False
        assert any("whitespace" in error.lower() for error in result.errors)
    
    def test_validate_sentence_word_count_mismatch(self):
        """Test validation detects word count mismatch."""
        sentence = Sentence(
            text="Bonjour tout le monde",
            domain="test",
            source_file="test.csv",
            line_number=1,
            char_count=21,
            word_count=10,  # Incorrect count
            metadata={}
        )
        
        validator = DataValidator()
        result = validator.validate_sentence(sentence)
        
        assert len(result.warnings) > 0
        assert any("word count" in warning.lower() for warning in result.warnings)
    
    def test_check_encoding_valid(self):
        """Test encoding check with valid text."""
        validator = DataValidator()
        
        assert validator.check_encoding("Bonjour, ça va?") is True
        assert validator.check_encoding("Texte avec accents: é, è, à, ù") is True
    
    def test_check_encoding_invalid(self):
        """Test encoding check with invalid text."""
        validator = DataValidator()
        
        assert validator.check_encoding("") is False
        assert validator.check_encoding("Text with null\x00byte") is False
        assert validator.check_encoding("Text with replacement\ufffdchar") is False
    
    def test_check_empty_or_whitespace(self):
        """Test empty/whitespace check."""
        validator = DataValidator()
        
        assert validator.check_empty_or_whitespace("Valid text") is True
        assert validator.check_empty_or_whitespace("") is False
        assert validator.check_empty_or_whitespace("   ") is False
        assert validator.check_empty_or_whitespace("\t\n") is False
    
    def test_sentence_integrity_excessive_whitespace(self):
        """Test detection of excessive whitespace."""
        sentence = Sentence(
            text="Phrase avec    trop    d'espaces",
            domain="test",
            source_file="test.csv",
            line_number=1,
            char_count=33,
            word_count=4,
            metadata={}
        )
        
        validator = DataValidator()
        result = validator.validate_sentence(sentence)
        
        assert any("whitespace" in warning.lower() for warning in result.warnings)
    
    def test_sentence_integrity_excessive_punctuation(self):
        """Test detection of excessive punctuation."""
        sentence = Sentence(
            text="Vraiment!!!",
            domain="test",
            source_file="test.csv",
            line_number=1,
            char_count=11,
            word_count=1,
            metadata={}
        )
        
        validator = DataValidator()
        result = validator.validate_sentence(sentence)
        
        assert any("punctuation" in warning.lower() for warning in result.warnings)


class TestDataModels:
    """Tests for data models."""
    
    def test_sentence_creation(self):
        """Test Sentence dataclass creation."""
        sentence = Sentence(
            text="Test sentence",
            domain="test",
            source_file="test.csv",
            line_number=1,
            char_count=13,
            word_count=2,
            metadata={"key": "value"}
        )
        
        assert sentence.text == "Test sentence"
        assert sentence.domain == "test"
        assert sentence.source_file == "test.csv"
        assert sentence.line_number == 1
        assert sentence.char_count == 13
        assert sentence.word_count == 2
        assert sentence.metadata["key"] == "value"
    
    def test_sentence_default_metadata(self):
        """Test Sentence with default metadata."""
        sentence = Sentence(
            text="Test",
            domain="test",
            source_file="test.csv",
            line_number=1,
            char_count=4,
            word_count=1
        )
        
        assert sentence.metadata == {}
    
    def test_validation_result_creation(self):
        """Test ValidationResult dataclass creation."""
        result = ValidationResult(
            is_valid=True,
            errors=["error1"],
            warnings=["warning1"]
        )
        
        assert result.is_valid is True
        assert result.errors == ["error1"]
        assert result.warnings == ["warning1"]
    
    def test_validation_result_defaults(self):
        """Test ValidationResult with default values."""
        result = ValidationResult(is_valid=False)
        
        assert result.is_valid is False
        assert result.errors == []
        assert result.warnings == []
