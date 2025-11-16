# Complete Example Language Pack

This is a complete example demonstrating all features of a Language Pack.

## Features

- Full configuration with all sections
- All threshold types configured
- All analyzers enabled
- Complete set of resource files:
  - Lexicon (10 words)
  - Stopwords (6 words)
  - Gender terms (masculine, feminine, neutral)
  - Gendered professions (3 examples)

## Purpose

This pack serves as:
1. A reference implementation
2. A testing fixture
3. Documentation by example

## Usage

```python
from langquality.language_packs import LanguagePackManager

manager = LanguagePackManager()
pack = manager.load_language_pack("cmp")
print(f"Loaded: {pack.name}")
print(f"Resources: {pack.list_resources()}")
```
