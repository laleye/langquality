"""Best practices constants for ASR and translation quality.

This module defines optimal thresholds and best practices based on research
in Automatic Speech Recognition (ASR) and machine translation for low-resource
languages. These thresholds are designed to ensure high-quality datasets for
training NLP models for low-resource languages.

References:
- ASR best practices for low-resource languages (Common Voice, Mozilla)
- Translation quality guidelines (FLORES, NLLB)
- Speech corpus design principles (LDC, ELRA)
"""


class BestPractices:
    """Best practices thresholds for dataset quality assessment.
    
    These constants define optimal ranges and thresholds for various quality
    metrics based on research in ASR and translation for low-resource languages.
    """
    
    # ========== Sentence Length ==========
    # Optimal range for clear pronunciation and accurate transcription
    # Shorter sentences (5-15 words) are easier to pronounce consistently
    # and reduce cognitive load for speakers during recording sessions
    OPTIMAL_SENTENCE_LENGTH = (5, 15)  # words
    
    # Absolute limits for sentence length
    # Sentences longer than 20 words are difficult to pronounce in one breath
    # and increase the risk of errors during recording
    MAX_SENTENCE_LENGTH = 20  # words
    
    # Sentences shorter than 3 words often lack sufficient context
    # for meaningful translation and may not represent natural language use
    MIN_SENTENCE_LENGTH = 3  # words
    
    # Warning threshold for sentences approaching the limits
    # Used to flag sentences that are close to being too long/short
    LENGTH_WARNING_THRESHOLD = 0.8  # 80% of max/min
    
    # ========== Vocabulary Diversity ==========
    # Target Type-Token Ratio (TTR) for vocabulary richness
    # TTR = unique_words / total_words
    # A TTR of 0.6 indicates good vocabulary diversity without excessive repetition
    TARGET_TTR = 0.6
    
    # Minimum acceptable TTR - below this indicates too much repetition
    MIN_TTR = 0.4
    
    # Ideal vocabulary coverage of common French words
    # Dataset should cover at least 70% of the most frequent 5000 French words
    TARGET_VOCABULARY_COVERAGE = 0.7
    
    # ========== Linguistic Complexity ==========
    # Maximum Flesch Reading Ease score (French adaptation)
    # Scores above 60 indicate text that is too complex for clear pronunciation
    # Lower scores (40-60) are optimal for ASR training data
    MAX_READABILITY_SCORE = 60
    OPTIMAL_READABILITY_SCORE = (40, 60)
    
    # Maximum acceptable lexical complexity (0.0-1.0)
    # Based on word frequency - higher values indicate more rare/technical words
    MAX_LEXICAL_COMPLEXITY = 0.7
    
    # Maximum percentage of sentences with complex syntax
    # Complex syntax can lead to pronunciation difficulties and translation errors
    MAX_COMPLEX_SYNTAX_PERCENTAGE = 0.2  # 20%
    
    # ========== Structural Diversity ==========
    # Minimum diversity score for sentence starters (0.0-1.0)
    # Higher diversity indicates more varied sentence structures
    MIN_STARTER_DIVERSITY = 0.5
    
    # Maximum acceptable repetition for n-grams
    # N-grams appearing more than this threshold indicate excessive repetition
    MAX_NGRAM_REPETITION_COUNT = 10
    
    # Similarity threshold for near-duplicate detection
    # Sentences with similarity above this are considered near-duplicates
    NEAR_DUPLICATE_THRESHOLD = 0.8
    
    # Maximum acceptable percentage of near-duplicate sentences
    MAX_NEAR_DUPLICATE_PERCENTAGE = 0.05  # 5%
    
    # ========== Domain Balance ==========
    # Minimum representation for each domain (10%)
    # Ensures all domains have sufficient coverage
    MIN_DOMAIN_REPRESENTATION = 0.10
    
    # Maximum representation for any single domain (30%)
    # Prevents over-representation of specific topics
    MAX_DOMAIN_REPRESENTATION = 0.30
    
    # Optimal domain representation range
    # Ideally, domains should be relatively balanced
    OPTIMAL_DOMAIN_REPRESENTATION = (0.15, 0.25)
    
    # ========== Gender Balance ==========
    # Target range for feminine/masculine ratio
    # Ratio between 0.4 and 0.6 indicates balanced gender representation
    TARGET_GENDER_RATIO = (0.4, 0.6)
    
    # Maximum acceptable bias score (0.0-1.0)
    # Scores above this threshold indicate significant gender bias
    MAX_BIAS_SCORE = 0.3
    
    # Maximum acceptable number of stereotypes per 100 sentences
    MAX_STEREOTYPES_PER_100 = 2
    
    # ========== Recommendation Priorities ==========
    # Priority levels for recommendations (1 = highest, 5 = lowest)
    PRIORITY_CRITICAL = 1  # Must fix - blocks dataset quality
    PRIORITY_HIGH = 2      # Should fix - significant impact on quality
    PRIORITY_MEDIUM = 3    # Should address - moderate impact
    PRIORITY_LOW = 4       # Nice to have - minor improvements
    PRIORITY_INFO = 5      # Informational - no action required
    
    # ========== Severity Levels ==========
    SEVERITY_CRITICAL = "critical"
    SEVERITY_WARNING = "warning"
    SEVERITY_INFO = "info"
