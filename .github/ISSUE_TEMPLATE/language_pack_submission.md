---
name: Language Pack Submission
about: Submit a new language pack for inclusion in LangQuality
title: '[LANGUAGE PACK] '
labels: language-pack, community
assignees: ''
---

## Language Information

- **Language Name**: [e.g., Yoruba]
- **ISO 639-3 Code**: [e.g., yor]
- **Language Family**: [e.g., Niger-Congo]
- **Script**: [e.g., Latin, Arabic, Devanagari]
- **Number of Speakers**: [approximate]
- **Geographic Region**: [where the language is spoken]

## Pack Completeness

Check all that apply:

- [ ] `config.yaml` with language configuration
- [ ] `metadata.json` with pack information
- [ ] Lexicon/frequency list
- [ ] Stopwords list
- [ ] Gender terms (if applicable)
- [ ] Profession terms (if applicable)
- [ ] Domain-specific resources
- [ ] Custom analyzers
- [ ] README with language-specific documentation
- [ ] Example data for testing

## Resources Included

Describe the linguistic resources you're providing:

**Lexicon:**
- Size: [number of entries]
- Source: [corpus, dictionary, etc.]
- License: [license information]

**Other Resources:**
- List other resources and their sources
- Provide licensing information for each

## Data Sources

List the sources used to create this language pack:

1. [Source name and URL]
2. [Source name and URL]

## Licensing

- **Language Pack License**: [e.g., MIT, CC-BY-4.0]
- **Resource Licenses**: [list licenses for each resource]
- [ ] I confirm I have the right to share these resources
- [ ] All resources are properly attributed
- [ ] Licenses are compatible with LangQuality's MIT license

## Testing

- [ ] I have tested the language pack with sample data
- [ ] All analyzers work as expected
- [ ] Configuration validates successfully
- [ ] I have included test data

**Test Results:**
```
Paste output from: langquality pack validate language_packs/XXX/
```

## Documentation

- [ ] README.md with language-specific information
- [ ] Usage examples
- [ ] Known limitations documented
- [ ] References to linguistic resources

## Community Impact

Describe how this language pack will benefit the community:
- Who will use this language pack?
- What research or applications will it enable?
- Are there existing tools for this language?

## Maintainer Information

- **Your Name/Organization**: 
- **Contact Email**: 
- **GitHub Username**: @
- [ ] I am willing to maintain this language pack
- [ ] I can provide support for users of this language pack

## Additional Context

Add any other context, research papers, or information about the language pack here.

## Checklist

Before submitting, please ensure:

- [ ] I have read the [Language Pack Guide](../docs/language_pack_guide.md)
- [ ] I have followed the [Contributing Guidelines](../CONTRIBUTING.md)
- [ ] The pack follows the standard directory structure
- [ ] All files are properly formatted (YAML, JSON)
- [ ] I have tested the pack locally
- [ ] I have included proper attribution and licensing
- [ ] The pack includes a comprehensive README

## Related Issues

Link to any related issues or discussions about this language.
