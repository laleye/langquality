"""Generic data loader supporting multiple file formats."""

import csv
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
import chardet
import logging

from .models import Sentence
from .tokenizers import Tokenizer, create_tokenizer
from ..utils.exceptions import DataLoadError
from ..language_packs.models import LanguagePack


class GenericDataLoader:
    """Language-agnostic data loader with multi-format support.
    
    Supports loading data from CSV, JSON, JSONL, and plain text files.
    Automatically detects file formats and text columns in CSV files.
    Integrates with Language Pack tokenization configuration.
    """
    
    def __init__(self, language_pack: Optional[LanguagePack] = None):
        """Initialize the generic data loader.
        
        Args:
            language_pack: Optional LanguagePack for language-specific configuration
        """
        self.language_pack = language_pack
        self.logger = logging.getLogger(self.__class__.__name__)
        self.tokenizer = self._initialize_tokenizer()
    
    def _initialize_tokenizer(self) -> Tokenizer:
        """Initialize tokenizer based on language pack configuration.
        
        Returns:
            Tokenizer instance
        """
        if self.language_pack and self.language_pack.config.tokenization:
            tokenization_config = self.language_pack.config.tokenization
            method = tokenization_config.method
            
            # Prepare config for tokenizer
            config = {}
            if tokenization_config.model:
                config['model'] = tokenization_config.model
            
            try:
                tokenizer = create_tokenizer(method, config)
                self.logger.info(f"Initialized {method} tokenizer")
                return tokenizer
            except Exception as e:
                self.logger.warning(
                    f"Failed to initialize {method} tokenizer: {e}. "
                    f"Falling back to whitespace tokenizer."
                )
                return create_tokenizer('whitespace')
        else:
            # Default to whitespace tokenizer
            return create_tokenizer('whitespace')
    
    def load(self, filepath: str, 
             text_column: Optional[str] = None,
             text_field: Optional[str] = None,
             domain: Optional[str] = None) -> List[Sentence]:
        """Load sentences from a file with automatic format detection.
        
        Args:
            filepath: Path to the file
            text_column: Column name for CSV files (auto-detected if None)
            text_field: Field name for JSON files (default: 'text')
            domain: Domain name (extracted from filename if None)
            
        Returns:
            List of Sentence objects
            
        Raises:
            DataLoadError: If file cannot be read or format not supported
        """
        if not os.path.exists(filepath):
            raise DataLoadError(f"File not found: {filepath}")
        
        # Auto-detect format
        file_format = self.auto_detect_format(filepath)
        
        # Extract domain from filename if not provided
        if domain is None:
            domain = self.extract_domain_from_filename(os.path.basename(filepath))
        
        # Load based on format
        if file_format == 'csv':
            return self.load_from_csv(filepath, text_column, domain)
        elif file_format == 'json':
            return self.load_from_json(filepath, text_field or 'text', domain)
        elif file_format == 'jsonl':
            return self.load_from_jsonl(filepath, text_field or 'text', domain)
        elif file_format == 'txt':
            return self.load_from_text(filepath, domain)
        else:
            raise DataLoadError(f"Unsupported file format: {file_format}")
    
    def auto_detect_format(self, filepath: str) -> str:
        """Auto-detect file format based on extension and content.
        
        Args:
            filepath: Path to the file
            
        Returns:
            Format string ('csv', 'json', 'jsonl', 'txt')
        """
        # Check extension first
        ext = Path(filepath).suffix.lower()
        
        if ext == '.csv':
            return 'csv'
        elif ext == '.json':
            # Could be JSON or JSONL, check content
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    if first_line.startswith('['):
                        return 'json'
                    elif first_line.startswith('{'):
                        return 'jsonl'
            except Exception:
                return 'json'  # Default to JSON
        elif ext == '.jsonl':
            return 'jsonl'
        elif ext in ['.txt', '.text']:
            return 'txt'
        else:
            # Try to detect from content
            return self._detect_format_from_content(filepath)
    
    def _detect_format_from_content(self, filepath: str) -> str:
        """Detect format by examining file content.
        
        Args:
            filepath: Path to the file
            
        Returns:
            Format string
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                
                # Check for JSON
                if first_line.startswith('[') or first_line.startswith('{'):
                    return 'json' if first_line.startswith('[') else 'jsonl'
                
                # Check for CSV (look for commas or tabs)
                if ',' in first_line or '\t' in first_line:
                    return 'csv'
                
                # Default to text
                return 'txt'
        except Exception:
            return 'txt'
    
    def load_from_csv(self, filepath: str, 
                      text_column: Optional[str] = None,
                      domain: Optional[str] = None) -> List[Sentence]:
        """Load sentences from a CSV file.
        
        Args:
            filepath: Path to the CSV file
            text_column: Column name containing text (auto-detected if None)
            domain: Domain name
            
        Returns:
            List of Sentence objects
            
        Raises:
            DataLoadError: If file cannot be read or parsed
        """
        # Detect encoding
        encoding = self._detect_encoding(filepath)
        
        # Extract domain from filename if not provided
        if domain is None:
            domain = self.extract_domain_from_filename(os.path.basename(filepath))
        
        sentences = []
        filename = os.path.basename(filepath)
        
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                # Try to detect if file has headers
                sample = f.read(1024)
                f.seek(0)
                
                sniffer = csv.Sniffer()
                try:
                    has_header = sniffer.has_header(sample)
                    dialect = sniffer.sniff(sample)
                except csv.Error:
                    has_header = False
                    dialect = csv.excel
                
                reader = csv.reader(f, dialect=dialect)
                
                # Read header if present
                header = None
                if has_header:
                    header = next(reader, None)
                
                # Auto-detect text column if not specified
                text_col_index = 0
                if text_column and header:
                    try:
                        text_col_index = header.index(text_column)
                    except ValueError:
                        raise DataLoadError(
                            f"Column '{text_column}' not found in CSV. "
                            f"Available columns: {header}"
                        )
                elif header:
                    # Auto-detect: look for common text column names
                    text_col_index = self._detect_text_column(header)
                
                # Read data rows
                start_line = 2 if has_header else 1
                for line_number, row in enumerate(reader, start=start_line):
                    if not row or len(row) <= text_col_index:
                        continue
                    
                    text = row[text_col_index].strip()
                    
                    if not text:
                        continue
                    
                    # Tokenize and calculate metrics
                    tokens = self.tokenizer.tokenize(text)
                    char_count = len(text)
                    word_count = len(tokens)
                    
                    sentence = Sentence(
                        text=text,
                        domain=domain,
                        source_file=filename,
                        line_number=line_number,
                        char_count=char_count,
                        word_count=word_count,
                        metadata={'tokens': tokens}
                    )
                    sentences.append(sentence)
                    
        except Exception as e:
            raise DataLoadError(f"Error reading CSV file {filepath}: {str(e)}")
        
        if not sentences:
            raise DataLoadError(f"No valid sentences found in {filepath}")
        
        return sentences
    
    def _detect_text_column(self, header: List[str]) -> int:
        """Auto-detect which column contains text data.
        
        Args:
            header: List of column names
            
        Returns:
            Index of the text column
        """
        # Common text column names (case-insensitive)
        text_column_names = [
            'text', 'sentence', 'content', 'phrase', 'utterance',
            'transcription', 'translation', 'source', 'target'
        ]
        
        header_lower = [col.lower() for col in header]
        
        for text_name in text_column_names:
            if text_name in header_lower:
                return header_lower.index(text_name)
        
        # If no match, use first column
        self.logger.warning(
            f"Could not auto-detect text column from header: {header}. "
            f"Using first column."
        )
        return 0
    
    def load_from_json(self, filepath: str, 
                       text_field: str = 'text',
                       domain: Optional[str] = None) -> List[Sentence]:
        """Load sentences from a JSON file (array of objects).
        
        Args:
            filepath: Path to the JSON file
            text_field: Field name containing text
            domain: Domain name
            
        Returns:
            List of Sentence objects
            
        Raises:
            DataLoadError: If file cannot be read or parsed
        """
        # Detect encoding
        encoding = self._detect_encoding(filepath)
        
        # Extract domain from filename if not provided
        if domain is None:
            domain = self.extract_domain_from_filename(os.path.basename(filepath))
        
        sentences = []
        filename = os.path.basename(filepath)
        
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                raise DataLoadError(
                    f"JSON file must contain an array of objects, got {type(data)}"
                )
            
            for line_number, item in enumerate(data, start=1):
                if not isinstance(item, dict):
                    self.logger.warning(
                        f"Skipping non-dict item at line {line_number}"
                    )
                    continue
                
                if text_field not in item:
                    self.logger.warning(
                        f"Field '{text_field}' not found at line {line_number}"
                    )
                    continue
                
                text = str(item[text_field]).strip()
                
                if not text:
                    continue
                
                # Tokenize and calculate metrics
                tokens = self.tokenizer.tokenize(text)
                char_count = len(text)
                word_count = len(tokens)
                
                # Extract additional metadata
                metadata = {k: v for k, v in item.items() if k != text_field}
                metadata['tokens'] = tokens
                
                sentence = Sentence(
                    text=text,
                    domain=domain,
                    source_file=filename,
                    line_number=line_number,
                    char_count=char_count,
                    word_count=word_count,
                    metadata=metadata
                )
                sentences.append(sentence)
                
        except json.JSONDecodeError as e:
            raise DataLoadError(f"Invalid JSON in {filepath}: {str(e)}")
        except Exception as e:
            raise DataLoadError(f"Error reading JSON file {filepath}: {str(e)}")
        
        if not sentences:
            raise DataLoadError(f"No valid sentences found in {filepath}")
        
        return sentences
    
    def load_from_jsonl(self, filepath: str, 
                        text_field: str = 'text',
                        domain: Optional[str] = None) -> List[Sentence]:
        """Load sentences from a JSONL file (one JSON object per line).
        
        Args:
            filepath: Path to the JSONL file
            text_field: Field name containing text
            domain: Domain name
            
        Returns:
            List of Sentence objects
            
        Raises:
            DataLoadError: If file cannot be read or parsed
        """
        # Detect encoding
        encoding = self._detect_encoding(filepath)
        
        # Extract domain from filename if not provided
        if domain is None:
            domain = self.extract_domain_from_filename(os.path.basename(filepath))
        
        sentences = []
        filename = os.path.basename(filepath)
        
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                for line_number, line in enumerate(f, start=1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        item = json.loads(line)
                    except json.JSONDecodeError:
                        self.logger.warning(
                            f"Invalid JSON at line {line_number}, skipping"
                        )
                        continue
                    
                    if not isinstance(item, dict):
                        self.logger.warning(
                            f"Non-dict item at line {line_number}, skipping"
                        )
                        continue
                    
                    if text_field not in item:
                        self.logger.warning(
                            f"Field '{text_field}' not found at line {line_number}"
                        )
                        continue
                    
                    text = str(item[text_field]).strip()
                    
                    if not text:
                        continue
                    
                    # Tokenize and calculate metrics
                    tokens = self.tokenizer.tokenize(text)
                    char_count = len(text)
                    word_count = len(tokens)
                    
                    # Extract additional metadata
                    metadata = {k: v for k, v in item.items() if k != text_field}
                    metadata['tokens'] = tokens
                    
                    sentence = Sentence(
                        text=text,
                        domain=domain,
                        source_file=filename,
                        line_number=line_number,
                        char_count=char_count,
                        word_count=word_count,
                        metadata=metadata
                    )
                    sentences.append(sentence)
                    
        except Exception as e:
            raise DataLoadError(f"Error reading JSONL file {filepath}: {str(e)}")
        
        if not sentences:
            raise DataLoadError(f"No valid sentences found in {filepath}")
        
        return sentences
    
    def load_from_text(self, filepath: str, 
                       domain: Optional[str] = None,
                       sentence_per_line: bool = True) -> List[Sentence]:
        """Load sentences from a plain text file.
        
        Args:
            filepath: Path to the text file
            domain: Domain name
            sentence_per_line: If True, treat each line as a sentence
            
        Returns:
            List of Sentence objects
            
        Raises:
            DataLoadError: If file cannot be read
        """
        # Detect encoding
        encoding = self._detect_encoding(filepath)
        
        # Extract domain from filename if not provided
        if domain is None:
            domain = self.extract_domain_from_filename(os.path.basename(filepath))
        
        sentences = []
        filename = os.path.basename(filepath)
        
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                if sentence_per_line:
                    # Each line is a sentence
                    for line_number, line in enumerate(f, start=1):
                        text = line.strip()
                        
                        if not text:
                            continue
                        
                        # Tokenize and calculate metrics
                        tokens = self.tokenizer.tokenize(text)
                        char_count = len(text)
                        word_count = len(tokens)
                        
                        sentence = Sentence(
                            text=text,
                            domain=domain,
                            source_file=filename,
                            line_number=line_number,
                            char_count=char_count,
                            word_count=word_count,
                            metadata={'tokens': tokens}
                        )
                        sentences.append(sentence)
                else:
                    # Read entire file as one text
                    text = f.read().strip()
                    
                    if text:
                        # Tokenize and calculate metrics
                        tokens = self.tokenizer.tokenize(text)
                        char_count = len(text)
                        word_count = len(tokens)
                        
                        sentence = Sentence(
                            text=text,
                            domain=domain,
                            source_file=filename,
                            line_number=1,
                            char_count=char_count,
                            word_count=word_count,
                            metadata={'tokens': tokens}
                        )
                        sentences.append(sentence)
                    
        except Exception as e:
            raise DataLoadError(f"Error reading text file {filepath}: {str(e)}")
        
        if not sentences:
            raise DataLoadError(f"No valid sentences found in {filepath}")
        
        return sentences
    
    def load_directory(self, dirpath: str, 
                       file_pattern: str = '*',
                       recursive: bool = False) -> Dict[str, List[Sentence]]:
        """Load sentences from all supported files in a directory.
        
        Args:
            dirpath: Path to directory
            file_pattern: Glob pattern for files (default: all files)
            recursive: If True, search subdirectories recursively
            
        Returns:
            Dictionary mapping domain names to lists of sentences
            
        Raises:
            DataLoadError: If directory doesn't exist or no files found
        """
        if not os.path.exists(dirpath):
            raise DataLoadError(f"Directory not found: {dirpath}")
        
        if not os.path.isdir(dirpath):
            raise DataLoadError(f"Path is not a directory: {dirpath}")
        
        # Find all matching files
        path = Path(dirpath)
        if recursive:
            files = list(path.rglob(file_pattern))
        else:
            files = list(path.glob(file_pattern))
        
        # Filter for supported formats
        supported_extensions = {'.csv', '.json', '.jsonl', '.txt', '.text'}
        files = [f for f in files if f.suffix.lower() in supported_extensions]
        
        if not files:
            raise DataLoadError(
                f"No supported files found in {dirpath} "
                f"(supported: {', '.join(supported_extensions)})"
            )
        
        all_sentences = {}
        
        for file_path in files:
            try:
                sentences = self.load(str(file_path))
                domain = self.extract_domain_from_filename(file_path.name)
                
                if domain not in all_sentences:
                    all_sentences[domain] = []
                
                all_sentences[domain].extend(sentences)
                self.logger.info(
                    f"Loaded {len(sentences)} sentences from {file_path.name}"
                )
                
            except DataLoadError as e:
                self.logger.warning(f"Skipping {file_path.name}: {str(e)}")
                continue
        
        if not all_sentences:
            raise DataLoadError(f"No valid sentences loaded from {dirpath}")
        
        return all_sentences
    
    def extract_domain_from_filename(self, filename: str) -> str:
        """Extract domain from filename.
        
        Removes file extension and cleans the name.
        
        Args:
            filename: Name of the file
            
        Returns:
            Domain name extracted from filename
        """
        # Remove extension
        domain = Path(filename).stem
        
        # Clean up the domain name
        domain = domain.strip()
        
        if not domain:
            domain = "unknown"
        
        return domain
    
    def _detect_encoding(self, filepath: str) -> str:
        """Detect file encoding using chardet.
        
        Args:
            filepath: Path to the file
            
        Returns:
            Detected encoding name (defaults to 'utf-8' if detection fails)
        """
        try:
            with open(filepath, 'rb') as f:
                raw_data = f.read(10000)  # Read first 10KB
                result = chardet.detect(raw_data)
                encoding = result['encoding']
                
                # Default to utf-8 if detection is uncertain
                if encoding is None or result['confidence'] < 0.7:
                    return 'utf-8'
                
                return encoding
        except Exception:
            # Default to utf-8 on any error
            return 'utf-8'
