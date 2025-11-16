"""Template generator for creating new Language Packs."""

import json
from datetime import datetime
from pathlib import Path

import yaml


class LanguagePackTemplate:
    """Generator for Language Pack templates."""
    
    @staticmethod
    def create_template(
        language_code: str,
        language_name: str,
        output_dir: Path,
        author: str = "Your Name",
        email: str = "your.email@example.com",
        minimal: bool = False
    ) -> Path:
        """Create a template Language Pack directory structure.
        
        Args:
            language_code: ISO 639-3 language code (e.g., 'fon', 'eng')
            language_name: Full language name (e.g., 'Fongbe', 'English')
            output_dir: Directory where the pack will be created
            author: Pack author name
            email: Author email
            minimal: If True, create minimal template; otherwise create complete template
            
        Returns:
            Path to created language pack directory
        """
        pack_dir = output_dir / language_code
        pack_dir.mkdir(parents=True, exist_ok=True)
        
        # Create config.yaml
        config_content = LanguagePackTemplate._generate_config(
            language_code, language_name, minimal
        )
        config_file = pack_dir / "config.yaml"
        with open(config_file, "w", encoding="utf-8") as f:
            yaml.dump(config_content, f, default_flow_style=False, sort_keys=False)
        
        # Create metadata.json
        metadata_content = LanguagePackTemplate._generate_metadata(
            author, email, language_name
        )
        metadata_file = pack_dir / "metadata.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata_content, f, indent=2, ensure_ascii=False)
        
        # Create resources directory
        resources_dir = pack_dir / "resources"
        resources_dir.mkdir(exist_ok=True)
        
        if not minimal:
            # Create example resource files
            LanguagePackTemplate._create_example_resources(resources_dir)
        
        # Create README
        readme_content = LanguagePackTemplate._generate_readme(
            language_code, language_name
        )
        readme_file = pack_dir / "README.md"
        with open(readme_file, "w", encoding="utf-8") as f:
            f.write(readme_content)
        
        return pack_dir
    
    @staticmethod
    def _generate_config(language_code: str, language_name: str, 
                        minimal: bool) -> dict:
        """Generate config.yaml content.
        
        Args:
            language_code: ISO 639-3 language code
            language_name: Full language name
            minimal: Whether to generate minimal config
            
        Returns:
            Dictionary with configuration
        """
        config = {
            "language": {
                "code": language_code,
                "name": language_name,
                "family": "Unknown",  # User should fill this in
                "script": "Latin",
                "direction": "ltr",
            },
            "tokenization": {
                "method": "whitespace",
                "model": None,
                "custom_rules": [],
            },
        }
        
        if not minimal:
            config["thresholds"] = {
                "structural": {
                    "min_words": 3,
                    "max_words": 20,
                    "min_chars": 10,
                    "max_chars": 200,
                },
                "linguistic": {
                    "max_readability_score": 60.0,
                    "enable_pos_tagging": True,
                    "enable_dependency_parsing": False,
                },
                "diversity": {
                    "target_ttr": 0.6,
                    "min_unique_words": 100,
                    "check_duplicates": True,
                },
                "domain": {
                    "min_representation": 0.10,
                    "max_representation": 0.30,
                    "balance_threshold": 0.15,
                },
                "gender": {
                    "target_ratio": [0.4, 0.6],
                    "check_stereotypes": True,
                },
            }
            
            config["analyzers"] = {
                "enabled": ["structural", "linguistic", "diversity", "domain"],
                "disabled": ["gender_bias"],
            }
            
            config["resources"] = {
                "lexicon": "lexicon.txt",
                "stopwords": "stopwords.txt",
                "gender_terms": "gender_terms.json",
                "professions": "professions.json",
                "custom": [],
            }
            
            config["plugins"] = []
        
        return config
    
    @staticmethod
    def _generate_metadata(author: str, email: str, language_name: str) -> dict:
        """Generate metadata.json content.
        
        Args:
            author: Pack author name
            email: Author email
            language_name: Full language name
            
        Returns:
            Dictionary with metadata
        """
        today = datetime.now().strftime("%Y-%m-%d")
        
        metadata = {
            "version": "0.1.0",
            "author": author,
            "email": email,
            "license": "MIT",
            "description": f"Language pack for {language_name}",
            "created": today,
            "updated": today,
            "contributors": [author],
            "status": "experimental",
            "coverage": {
                "lexicon_size": 0,
                "domains_covered": [],
                "has_gender_resources": False,
            },
            "dependencies": {
                "min_langquality_version": "1.0.0",
            },
            "references": [],
        }
        
        return metadata
    
    @staticmethod
    def _create_example_resources(resources_dir: Path):
        """Create example resource files.
        
        Args:
            resources_dir: Path to resources directory
        """
        # Create example lexicon
        lexicon_file = resources_dir / "lexicon.txt"
        with open(lexicon_file, "w", encoding="utf-8") as f:
            f.write("# Frequency lexicon - one word per line\n")
            f.write("# Format: word\n")
            f.write("# Example:\n")
            f.write("# hello\n")
            f.write("# world\n")
        
        # Create example stopwords
        stopwords_file = resources_dir / "stopwords.txt"
        with open(stopwords_file, "w", encoding="utf-8") as f:
            f.write("# Stopwords - one word per line\n")
            f.write("# Example:\n")
            f.write("# the\n")
            f.write("# a\n")
            f.write("# an\n")
        
        # Create example gender terms
        gender_terms_file = resources_dir / "gender_terms.json"
        gender_terms = {
            "masculine": ["he", "him", "his"],
            "feminine": ["she", "her", "hers"],
            "neutral": ["they", "them", "their"],
        }
        with open(gender_terms_file, "w", encoding="utf-8") as f:
            json.dump(gender_terms, f, indent=2, ensure_ascii=False)
        
        # Create example professions
        professions_file = resources_dir / "professions.json"
        professions = {
            "professions": [
                {
                    "neutral": "teacher",
                    "masculine": "male teacher",
                    "feminine": "female teacher",
                },
                {
                    "neutral": "doctor",
                    "masculine": "male doctor",
                    "feminine": "female doctor",
                },
            ]
        }
        with open(professions_file, "w", encoding="utf-8") as f:
            json.dump(professions, f, indent=2, ensure_ascii=False)
        
        # Create .gitkeep for custom directory
        custom_dir = resources_dir / "custom"
        custom_dir.mkdir(exist_ok=True)
        gitkeep = custom_dir / ".gitkeep"
        with open(gitkeep, "w") as f:
            f.write("# Place custom resource files here\n")
    
    @staticmethod
    def _generate_readme(language_code: str, language_name: str) -> str:
        """Generate README.md content.
        
        Args:
            language_code: ISO 639-3 language code
            language_name: Full language name
            
        Returns:
            README content as string
        """
        readme = f"""# Language Pack: {language_name} ({language_code})

This is a Language Pack for LangQuality, providing language-specific resources and configuration for {language_name}.

## Structure

```
{language_code}/
├── config.yaml          # Main configuration file
├── metadata.json        # Pack metadata
├── resources/           # Language-specific resources
│   ├── lexicon.txt      # Frequency lexicon (optional)
│   ├── stopwords.txt    # Stopwords list (optional)
│   ├── gender_terms.json # Gender-related terms (optional)
│   ├── professions.json  # Gendered professions (optional)
│   └── custom/          # Custom resources
└── README.md           # This file
```

## Configuration

Edit `config.yaml` to customize:

- **Language metadata**: Update family, script, and direction
- **Tokenization**: Choose tokenization method (spacy, nltk, whitespace, custom)
- **Thresholds**: Adjust analysis thresholds for your language
- **Analyzers**: Enable/disable specific analyzers
- **Resources**: Specify which resource files to use

## Resources

Add language-specific resources to the `resources/` directory:

1. **lexicon.txt**: Frequency lexicon (one word per line)
2. **stopwords.txt**: Common stopwords (one word per line)
3. **gender_terms.json**: Gender-related terms in JSON format
4. **professions.json**: Gendered professions in JSON format
5. **custom/**: Any additional custom resources

All resources are optional. Analyzers will gracefully degrade if resources are missing.

## Usage

```python
from langquality.language_packs import LanguagePackManager

manager = LanguagePackManager()
pack = manager.load_language_pack("{language_code}")
```

Or via CLI:

```bash
langquality analyze --language {language_code} input.csv
```

## Contributing

To improve this language pack:

1. Add more comprehensive resources
2. Adjust thresholds based on language characteristics
3. Add custom analyzers if needed
4. Update metadata with coverage information

## License

See the main LangQuality project for license information.
"""
        return readme


class InvalidPackTemplate:
    """Generator for invalid Language Pack templates (for testing)."""
    
    @staticmethod
    def create_invalid_template(output_dir: Path, error_type: str) -> Path:
        """Create an invalid Language Pack for testing validation.
        
        Args:
            output_dir: Directory where the pack will be created
            error_type: Type of error to introduce
                       ('missing_config', 'missing_metadata', 'invalid_yaml',
                        'invalid_json', 'invalid_code', 'invalid_structure')
            
        Returns:
            Path to created invalid pack directory
        """
        pack_dir = output_dir / "invalid_test"
        pack_dir.mkdir(parents=True, exist_ok=True)
        
        if error_type == "missing_config":
            # Create only metadata
            metadata = {"version": "1.0.0", "author": "Test", "email": "test@test.com", "license": "MIT"}
            with open(pack_dir / "metadata.json", "w") as f:
                json.dump(metadata, f)
        
        elif error_type == "missing_metadata":
            # Create only config
            config = {"language": {"code": "tst", "name": "Test"}}
            with open(pack_dir / "config.yaml", "w") as f:
                yaml.dump(config, f)
        
        elif error_type == "invalid_yaml":
            # Create invalid YAML
            with open(pack_dir / "config.yaml", "w") as f:
                f.write("language:\n  code: tst\n  name: Test\n  invalid: [unclosed")
            metadata = {"version": "1.0.0", "author": "Test", "email": "test@test.com", "license": "MIT"}
            with open(pack_dir / "metadata.json", "w") as f:
                json.dump(metadata, f)
        
        elif error_type == "invalid_json":
            # Create invalid JSON
            config = {"language": {"code": "tst", "name": "Test"}}
            with open(pack_dir / "config.yaml", "w") as f:
                yaml.dump(config, f)
            with open(pack_dir / "metadata.json", "w") as f:
                f.write('{"version": "1.0.0", "author": "Test", invalid}')
        
        elif error_type == "invalid_code":
            # Create config with invalid language code
            config = {"language": {"code": "invalid123", "name": "Test"}}
            with open(pack_dir / "config.yaml", "w") as f:
                yaml.dump(config, f)
            metadata = {"version": "1.0.0", "author": "Test", "email": "test@test.com", "license": "MIT"}
            with open(pack_dir / "metadata.json", "w") as f:
                json.dump(metadata, f)
        
        elif error_type == "invalid_structure":
            # Create config missing required fields
            config = {"language": {"name": "Test"}}  # Missing 'code'
            with open(pack_dir / "config.yaml", "w") as f:
                yaml.dump(config, f)
            metadata = {"version": "1.0.0", "author": "Test", "email": "test@test.com", "license": "MIT"}
            with open(pack_dir / "metadata.json", "w") as f:
                json.dump(metadata, f)
        
        return pack_dir
