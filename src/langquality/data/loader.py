"""CSV data loader."""

import csv
import os
from pathlib import Path
from typing import Dict, List
import chardet

from .models import Sentence
from ..utils.exceptions import DataLoadError


class DataLoader:
    """Loads data from CSV files.
    
    Handles CSV file loading with automatic encoding detection and domain extraction.
    """
    
    def load_csv(self, filepath: str) -> List[Sentence]:
        """Load sentences from a CSV file.
        
        Args:
            filepath: Path to the CSV file
            
        Returns:
            List of Sentence objects
            
        Raises:
            DataLoadError: If file cannot be read or parsed
        """
        if not os.path.exists(filepath):
            raise DataLoadError(f"File not found: {filepath}")
        
        # Detect encoding
        encoding = self._detect_encoding(filepath)
        
        # Extract domain from filename
        filename = os.path.basename(filepath)
        domain = self.extract_domain_from_filename(filename)
        
        sentences = []
        
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                # Try to detect if file has headers
                sample = f.read(1024)
                f.seek(0)
                
                sniffer = csv.Sniffer()
                try:
                    has_header = sniffer.has_header(sample)
                except csv.Error:
                    has_header = False
                
                reader = csv.reader(f)
                
                # Skip header if present
                if has_header:
                    next(reader, None)
                
                for line_number, row in enumerate(reader, start=2 if has_header else 1):
                    if not row:  # Skip empty rows
                        continue
                    
                    # Get text from first column
                    text = row[0].strip() if row else ""
                    
                    if not text:  # Skip empty text
                        continue
                    
                    # Calculate metrics
                    char_count = len(text)
                    word_count = len(text.split())
                    
                    sentence = Sentence(
                        text=text,
                        domain=domain,
                        source_file=filename,
                        line_number=line_number,
                        char_count=char_count,
                        word_count=word_count,
                        metadata={}
                    )
                    sentences.append(sentence)
                    
        except Exception as e:
            raise DataLoadError(f"Error reading CSV file {filepath}: {str(e)}")
        
        if not sentences:
            raise DataLoadError(f"No valid sentences found in {filepath}")
        
        return sentences
    
    def load_directory(self, dirpath: str) -> Dict[str, List[Sentence]]:
        """Load sentences from all CSV files in a directory.
        
        Args:
            dirpath: Path to directory containing CSV files
            
        Returns:
            Dictionary mapping domain names to lists of sentences
            
        Raises:
            DataLoadError: If directory doesn't exist or no CSV files found
        """
        if not os.path.exists(dirpath):
            raise DataLoadError(f"Directory not found: {dirpath}")
        
        if not os.path.isdir(dirpath):
            raise DataLoadError(f"Path is not a directory: {dirpath}")
        
        # Find all CSV files
        csv_files = list(Path(dirpath).glob("*.csv"))
        
        if not csv_files:
            raise DataLoadError(f"No CSV files found in {dirpath}")
        
        all_sentences = {}
        
        for csv_file in csv_files:
            try:
                sentences = self.load_csv(str(csv_file))
                domain = self.extract_domain_from_filename(csv_file.name)
                
                if domain not in all_sentences:
                    all_sentences[domain] = []
                
                all_sentences[domain].extend(sentences)
                
            except DataLoadError as e:
                # Log error but continue with other files
                print(f"Warning: Skipping {csv_file.name}: {str(e)}")
                continue
        
        if not all_sentences:
            raise DataLoadError(f"No valid sentences loaded from {dirpath}")
        
        return all_sentences
    
    def extract_domain_from_filename(self, filename: str) -> str:
        """Extract domain from filename.
        
        Extracts the domain by removing the .csv extension and cleaning the name.
        Examples:
            - "health_sentences.csv" -> "health_sentences"
            - "education.csv" -> "education"
            - "commerce-data.csv" -> "commerce-data"
        
        Args:
            filename: Name of the CSV file
            
        Returns:
            Domain name extracted from filename
        """
        # Remove .csv extension
        domain = filename
        if domain.lower().endswith('.csv'):
            domain = domain[:-4]
        
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
