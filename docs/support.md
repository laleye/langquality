# Support

Welcome to LangQuality support! We're here to help you get the most out of the Language Quality Toolkit.

## Getting Help

### 📚 Documentation

Before reaching out, check if your question is answered in our documentation:

- **[Quickstart Guide](quickstart.md)**: Get started quickly with LangQuality
- **[User Guide](user_guide/)**: Comprehensive guides for common tasks
- **[Language Pack Guide](language_pack_guide.md)**: Create and customize language packs
- **[FAQ](faq.md)**: Frequently asked questions
- **[API Reference](api_reference/)**: Detailed API documentation
- **[Developer Guide](developer_guide/)**: For contributors and plugin developers

### 💬 Community Support

#### GitHub Discussions (Recommended)

Our primary support channel is [GitHub Discussions](https://github.com/langquality/langquality-toolkit/discussions):

- **Q&A**: Ask questions and get help from the community
- **Ideas**: Propose new features and improvements
- **Language Packs**: Discuss language pack development
- **Show and Tell**: Share your projects and use cases

**Why Discussions?**
- Searchable archive helps future users
- Community members can help each other
- Maintainers monitor and respond regularly
- Threaded conversations keep discussions organized

#### Stack Overflow

Tag your questions with `langquality` and `nlp`:
- Good for specific technical questions
- Reaches a broader developer audience
- Searchable by search engines

### 🐛 Bug Reports

Found a bug? Please [open an issue](https://github.com/langquality/langquality-toolkit/issues/new?template=bug_report.md) with:

- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version, LangQuality version)
- Relevant code snippets or error messages

**Before reporting:**
1. Search existing issues to avoid duplicates
2. Update to the latest version
3. Check if it's a known issue in the [CHANGELOG](../CHANGELOG.md)

### 💡 Feature Requests

Have an idea for a new feature? We'd love to hear it!

1. **Check existing requests**: Search [GitHub Issues](https://github.com/langquality/langquality-toolkit/issues) and [Discussions](https://github.com/langquality/langquality-toolkit/discussions)
2. **Start a discussion**: Share your idea in the [Ideas category](https://github.com/langquality/langquality-toolkit/discussions/categories/ideas)
3. **Provide context**: Explain the use case and why it would be valuable
4. **Consider contributing**: We welcome pull requests!

### 🌍 Language Pack Submissions

Want to contribute a language pack?

1. **Review the guide**: Read our [Language Pack Guide](language_pack_guide.md)
2. **Use the template**: Start with the [template pack](../src/langquality/language_packs/packs/_template/)
3. **Test thoroughly**: Validate your pack with `langquality pack validate`
4. **Submit**: Open a [Language Pack Submission issue](https://github.com/langquality/langquality-toolkit/issues/new?template=language_pack_submission.md)

## Response Times

We're a community-driven project, so response times vary:

- **Critical bugs**: 24-48 hours
- **General questions**: 2-5 days
- **Feature requests**: 1-2 weeks for initial feedback
- **Pull requests**: 1 week for initial review

**Note**: These are goals, not guarantees. We're all volunteers!

## Commercial Support

Currently, LangQuality is a community-supported project. For commercial support options:

- **Consulting**: Contact the maintainers for custom development or consulting
- **Training**: We can provide training sessions for teams
- **Priority support**: Sponsorship options may be available

Contact: [community@langquality.org](mailto:community@langquality.org)

## Self-Help Resources

### Common Issues

#### Installation Problems

```bash
# Ensure you have Python 3.8+
python --version

# Upgrade pip
pip install --upgrade pip

# Install in a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install langquality
```

#### Import Errors

```python
# Correct import
from langquality import PipelineController
from langquality.language_packs import LanguagePackManager

# Legacy import (deprecated)
from fongbe_quality import PipelineController  # Shows deprecation warning
```

#### Language Pack Not Found

```bash
# List available packs
langquality pack list

# Validate pack location
langquality pack info <language_code>

# Check pack structure
langquality pack validate /path/to/pack
```

### Debugging Tips

1. **Enable verbose logging**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. **Check configuration**:
```bash
langquality --version
langquality pack list
```

3. **Validate your data**:
```bash
# Check file format
file your_data.csv

# Preview first few lines
head your_data.csv
```

4. **Test with minimal example**:
```python
from langquality import PipelineController
from langquality.language_packs import LanguagePackManager

# Load language pack
manager = LanguagePackManager()
pack = manager.load_language_pack("eng")

# Test with simple data
sentences = [{"text": "Hello world", "domain": "test"}]
controller = PipelineController(pack)
results = controller.run(sentences)
print(results)
```

## Contributing to Support

Help us help others!

### Answer Questions

- Monitor [GitHub Discussions](https://github.com/langquality/langquality-toolkit/discussions)
- Answer questions on Stack Overflow
- Share your expertise with the community

### Improve Documentation

- Fix typos and unclear explanations
- Add examples and use cases
- Translate documentation to other languages
- Update outdated information

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

### Share Your Experience

- Write blog posts about using LangQuality
- Create video tutorials
- Present at conferences or meetups
- Share on social media

## Code of Conduct

All support interactions are governed by our [Code of Conduct](../CODE_OF_CONDUCT.md). We're committed to providing a welcoming and inclusive environment for everyone.

## Security Issues

**Do not report security vulnerabilities publicly.**

If you discover a security issue, please email [security@langquality.org](mailto:security@langquality.org) with:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We'll respond within 48 hours and work with you to address the issue.

## Stay Updated

- **GitHub**: Watch the repository for updates
- **Releases**: Subscribe to [release notifications](https://github.com/langquality/langquality-toolkit/releases)
- **Discussions**: Follow topics you're interested in
- **Twitter**: Follow [@langquality](https://twitter.com/langquality) (if available)
- **Newsletter**: Subscribe to our quarterly newsletter (coming soon)

## Acknowledgments

Thank you to everyone who contributes to supporting the LangQuality community! Your questions, answers, and feedback make this project better for everyone.

## Additional Resources

- **[Roadmap](roadmap.md)**: See what's coming next
- **[Maintainers](maintainers.md)**: Meet the team
- **[Governance](../GOVERNANCE.md)**: How decisions are made
- **[Contributing](../CONTRIBUTING.md)**: How to contribute
- **[Migration Guide](migration_guide.md)**: Upgrading from older versions

---

**Last Updated**: 2024-03-20

**Questions about this document?** Open a discussion in the [Documentation category](https://github.com/langquality/langquality-toolkit/discussions/categories/documentation).
