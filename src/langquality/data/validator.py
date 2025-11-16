"""Data validator."""

import re
from typing import List

from .models import Sentence, ValidationResult


class DataValidator:
    """Validates data integrity.
    
    Performs validation checks on sentences to ensure data quality.
    """
    
    def validate_sentence(self, sentence: Sentence) -> ValidationResult:
        """Validate a sentence.
        
        Performs multiple validation checks:
        - Text encoding validity
        - Empty or whitespace-only text
        - Sentence integrity (basic structure)
        
        Args:
            sentence: Sentence object to validate
            
        Returns:
            ValidationResult with validation status and any errors/warnings
        """
        errors = []
        warnings = []
        
        # Check if text is empty or whitespace
        if not self.check_empty_or_whitespace(sentence.text):
            errors.append(f"Line {sentence.line_number}: Text is empty or contains only whitespace")
        
        # Check encoding validity
        if not self.check_encoding(sentence.text):
            errors.append(f"Line {sentence.line_number}: Text contains invalid characters or encoding issues")
        
        # Check sentence integrity
        integrity_issues = self._check_sentence_integrity(sentence.text)
        if integrity_issues:
            warnings.extend([f"Line {sentence.line_number}: {issue}" for issue in integrity_issues])
        
        # Check word count consistency
        if sentence.word_count != len(sentence.text.split()):
            warnings.append(f"Line {sentence.line_number}: Word count mismatch")
        
        # Check character count consistency
        if sentence.char_count != len(sentence.text):
            warnings.append(f"Line {sentence.line_number}: Character count mismatch")
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings
        )
    
    def check_encoding(self, text: str) -> bool:
        """Check text encoding validity.
        
        Verifies that the text can be properly encoded/decoded and doesn't
        contain problematic characters.
        
        Args:
            text: Text to check
            
        Returns:
            True if encoding is valid, False otherwise
        """
        if not text:
            return False
        
        try:
            # Try to encode/decode to verify encoding integrity
            text.encode('utf-8').decode('utf-8')
            
            # Check for null bytes or other problematic characters
            if '\x00' in text:
                return False
            
            # Check for replacement characters (indicates encoding issues)
            if '\ufffd' in text:
                return False
            
            return True
            
        except (UnicodeEncodeError, UnicodeDecodeError):
            return False
    
    def check_empty_or_whitespace(self, text: str) -> bool:
        """Check if text is empty or whitespace.
        
        Args:
            text: Text to check
            
        Returns:
            True if text has content, False if empty or whitespace-only
        """
        if not text:
            return False
        
        if not text.strip():
            return False
        
        return True
    
    def _check_sentence_integrity(self, text: str) -> List[str]:
        """Check sentence integrity and structure.
        
        Performs basic checks for sentence quality:
        - Excessive whitespace
        - Repeated punctuation
        - Unusual character patterns
        
        Args:
            text: Text to check
            
        Returns:
            List of integrity issues found (empty if no issues)
        """
        issues = []
        
        # Check for excessive whitespace
        if re.search(r'\s{3,}', text):
            issues.append("Contains excessive whitespace")
        
        # Check for repeated punctuation (e.g., "!!!", "???")
        if re.search(r'[!?\.]{3,}', text):
            issues.append("Contains excessive punctuation")
        
        # Check for unusual character repetition (e.g., "aaaaaaa")
        if re.search(r'(.)\1{5,}', text):
            issues.append("Contains unusual character repetition")
        
        # Check for mixed scripts (potential encoding issues)
        # This is a simple check - could be expanded
        has_latin = bool(re.search(r'[a-zA-ZÀ-ÿ]', text))
        has_cyrillic = bool(re.search(r'[А-Яа-я]', text))
        has_arabic = bool(re.search(r'[\u0600-\u06FF]', text))
        has_chinese = bool(re.search(r'[\u4e00-\u9fff]', text))
        
        script_count = sum([has_latin, has_cyrillic, has_arabic, has_chinese])
        if script_count > 1:
            issues.append("Contains mixed scripts (potential encoding issue)")
        
        # Check for control characters (except common whitespace)
        if re.search(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', text):
            issues.append("Contains control characters")
        
        return issues
