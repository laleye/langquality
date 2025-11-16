# Data Loading Guide

## Overview

The LangQuality toolkit provides a flexible, language-agnostic data loading system that supports multiple file formats and configurable tokenization.

## Key Components

### 1. Tokenization System

The tokenization system provides multiple tokenizer implementations:

#### Available Tokenizers

- **WhitespaceTokenizer**: Simple whitespace-based splitting (default, no dependencies)
- **SpacyTokenizer**: Linguistic-aware tokenization using spaCy models
- **NLTKTokenizer**: NLTK-based tokenization
- **CustomTokenizer**: User-defined tokenization function

#### Usage

```python
from langquality.data.tokenizers import create_tokenizer

# Create a whitespace tokenizer
tokenizer = create_tokenizer('whitespace')
tokens = tokenizer.tokenize('Hello world, this is a test.')
# Result: ['Hello', 'world,', 'this', 'is', 'a', 'test.']

# Create a spaCy tokenizer
tokenizer = create_tokenizer('spacy', {'model': 'fr_core_news_md'})
tokens = tokenizer.tokenize('Bonjour, comment allez-vous?')
# Result: ['Bonjour', ',', 'comment', 'allez', '-vous', '?']

# Create a custom tokenizer
def my_tokenizer(text):
    return text.lower().split()

tokenizer = create_tokenizer('custom', {'tokenize_fn': my_tokenizer})
tokens = tokenizer.tokenize('Hello World')
# Result: ['hello', 'world']
```

### 2. GenericDataLoader

The `GenericDataLoader` class provides multi-format data loading with automatic format detection.

#### Supported Formats

- **CSV**: Comma-separated values with automatic column detection
- **JSON**: JSON arrays of objects
- **JSONL**: JSON Lines (one JSON object per line)
- **TXT**: Plain text files (one sentence per line)

#### Basic Usage

```python
from langquality.data import GenericDataLoader

# Create loader (uses whitespace tokenizer by default)
loader = GenericDataLoader()

# Load from any supported format (auto-detected)
sentences = loader.load('data/sentences.csv')
sentences = loader.load('data/sentences.json')
sentences = loader.load('data/sentences.jsonl')
sentences = loader.load('data/sentences.txt')

# Access sentence data
for sentence in sentences:
    print(f"Text: {sentence.text}")
    print(f"Words: {sentence.word_count}")
    print(f"Domain: {sentence.domain}")
```

#### CSV Loading

```python
# Auto-detect text column
sentences = loader.load('data.csv')

# Specify text column explicitly
sentences = loader.load_from_csv('data.csv', text_column='sentence')

# Specify domain
sentences = loader.load('data.csv', domain='health')
```

The loader automatically detects common text column names:
- text, sentence, content, phrase, utterance
- transcription, translation, source, target

#### JSON Loading

```python
# Load JSON array
# File: [{"text": "sentence 1"}, {"text": "sentence 2"}]
sentences = loader.load('data.json')

# Specify custom text field
sentences = loader.load_from_json('data.json', text_field='content')
```

#### JSONL Loading

```python
# Load JSONL file
# File: {"text": "sentence 1"}
#       {"text": "sentence 2"}
sentences = loader.load('data.jsonl')

# Specify custom text field
sentences = loader.load_from_jsonl('data.jsonl', text_field='utterance')
```

#### Text File Loading

```python
# Load text file (one sentence per line)
sentences = loader.load('data.txt')

# Load entire file as one sentence
sentences = loader.load_from_text('data.txt', sentence_per_line=False)
```

#### Directory Loading

```python
# Load all supported files from a directory
all_sentences = loader.load_directory('data/')

# Result: {'domain1': [sentences...], 'domain2': [sentences...]}

# Load with pattern matching
all_sentences = loader.load_directory('data/', file_pattern='*.csv')

# Recursive loading
all_sentences = loader.load_directory('data/', recursive=True)
```

### 3. Language Pack Integration

The `GenericDataLoader` integrates with Language Packs to use language-specific tokenization:

```python
from langquality.data import GenericDataLoader
from langquality.language_packs import LanguagePackManager

# Load a language pack
manager = LanguagePackManager()
fon_pack = manager.load_language_pack('fon')

# Create loader with language pack
loader = GenericDataLoader(language_pack=fon_pack)

# The loader will use the tokenization method specified in the pack
sentences = loader.load('data.csv')
```

The tokenizer is automatically configured based on the language pack's `tokenization` settings:

```yaml
# In language pack config.yaml
tokenization:
  method: "spacy"
  model: "fr_core_news_md"
```

## Advanced Features

### Automatic Format Detection

The loader automatically detects file format based on:
1. File extension (.csv, .json, .jsonl, .txt)
2. File content (if extension is ambiguous)

```python
# All of these work automatically
loader.load('data.csv')    # Detected as CSV
loader.load('data.json')   # Detected as JSON
loader.load('data.jsonl')  # Detected as JSONL
loader.load('data.txt')    # Detected as text
```

### Encoding Detection

The loader automatically detects file encoding using `chardet`:

```python
# Works with various encodings
sentences = loader.load('utf8_file.csv')
sentences = loader.load('latin1_file.csv')
sentences = loader.load('utf16_file.csv')
```

### Error Handling

The loader provides clear error messages:

```python
from langquality.utils.exceptions import DataLoadError

try:
    sentences = loader.load('missing_file.csv')
except DataLoadError as e:
    print(f"Error: {e}")
```

## Migration from Old DataLoader

If you're migrating from the old `DataLoader` class:

```python
# Old way
from langquality.data import DataLoader
loader = DataLoader()
sentences = loader.load_csv('data.csv')

# New way (backward compatible)
from langquality.data import GenericDataLoader
loader = GenericDataLoader()
sentences = loader.load('data.csv')  # Auto-detects CSV format
```

The `GenericDataLoader` is backward compatible with CSV loading but adds support for multiple formats.

## Best Practices

1. **Use Language Packs**: Always use a language pack when available for better tokenization
2. **Specify Text Columns**: For CSV files with multiple columns, explicitly specify the text column
3. **Handle Errors**: Always wrap loading in try-except blocks for production code
4. **Use Directory Loading**: For large datasets, use `load_directory()` to process multiple files
5. **Check Sentence Metadata**: The loader preserves additional fields from JSON/JSONL in `sentence.metadata`

## Examples

### Example 1: Multi-format Dataset

```python
from langquality.data import GenericDataLoader

loader = GenericDataLoader()

# Load from different formats
csv_sentences = loader.load('train.csv')
json_sentences = loader.load('validation.json')
txt_sentences = loader.load('test.txt')

# Combine all sentences
all_sentences = csv_sentences + json_sentences + txt_sentences
```

### Example 2: Language-Specific Processing

```python
from langquality.data import GenericDataLoader
from langquality.language_packs import LanguagePackManager

# Load language pack
manager = LanguagePackManager()
pack = manager.load_language_pack('fon')

# Create loader with language-specific tokenization
loader = GenericDataLoader(language_pack=pack)

# Load and process
sentences = loader.load('fongbe_data.csv')

# Tokens are automatically computed using the pack's tokenizer
for sentence in sentences:
    print(f"{sentence.text}: {sentence.metadata['tokens']}")
```

### Example 3: Batch Processing

```python
from langquality.data import GenericDataLoader
from pathlib import Path

loader = GenericDataLoader()

# Process all files in a directory
data_dir = Path('datasets/')
all_data = loader.load_directory(str(data_dir), recursive=True)

# Process by domain
for domain, sentences in all_data.items():
    print(f"Domain: {domain}")
    print(f"  Sentences: {len(sentences)}")
    print(f"  Avg words: {sum(s.word_count for s in sentences) / len(sentences):.1f}")
```

## Troubleshooting

### SpaCy Model Not Found

If you get an error about missing spaCy models:

```bash
python -m spacy download fr_core_news_md
```

### NLTK Data Not Found

If you get an error about missing NLTK data:

```python
import nltk
nltk.download('punkt')
```

### Encoding Issues

If you encounter encoding issues, the loader will automatically try UTF-8. For specific encodings, you can pre-process files or open an issue.

### CSV Column Detection

If the loader can't detect the text column, specify it explicitly:

```python
sentences = loader.load_from_csv('data.csv', text_column='my_text_column')
```
