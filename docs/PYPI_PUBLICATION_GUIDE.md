# PyPI Publication Guide

This guide explains how to publish LangQuality to PyPI (Python Package Index) and TestPyPI.

## Prerequisites

### 1. PyPI Account Setup

1. **Create PyPI Account**
   - Go to https://pypi.org/account/register/
   - Create an account with a strong password
   - Verify your email address

2. **Create TestPyPI Account**
   - Go to https://test.pypi.org/account/register/
   - Create a separate account (TestPyPI is independent from PyPI)
   - Verify your email address

3. **Enable Two-Factor Authentication (2FA)**
   - Go to Account Settings on both PyPI and TestPyPI
   - Enable 2FA for security (required for trusted publishers)

### 2. GitHub Repository Setup

The release workflow uses **Trusted Publishers** (OIDC), which is more secure than API tokens.

#### Configure PyPI Trusted Publisher

1. Go to https://pypi.org/manage/account/publishing/
2. Click "Add a new pending publisher"
3. Fill in the details:
   - **PyPI Project Name**: `langquality`
   - **Owner**: Your GitHub username or organization
   - **Repository name**: `langquality`
   - **Workflow name**: `release.yml`
   - **Environment name**: `pypi`
4. Click "Add"

#### Configure TestPyPI Trusted Publisher

1. Go to https://test.pypi.org/manage/account/publishing/
2. Click "Add a new pending publisher"
3. Fill in the same details as above, but use environment name: `testpypi`
4. Click "Add"

### 3. GitHub Environments

Create two GitHub environments with protection rules:

1. Go to your repository → Settings → Environments
2. Create environment `pypi`:
   - Add protection rule: Require approval from maintainers
   - Add protection rule: Restrict to `main` branch
3. Create environment `testpypi`:
   - No protection rules needed (for testing)

## Testing the Package Locally

Before publishing, always test the package locally:

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build the package
python -m build

# Check the distribution
twine check dist/*

# Install locally and test
pip install dist/*.whl
langquality --help
langquality pack list

# Run tests
pytest tests/
```

## Publishing to TestPyPI

TestPyPI is a separate instance of PyPI for testing. Always test here first!

### Method 1: Using GitHub Actions (Recommended)

1. Go to your repository → Actions → Release workflow
2. Click "Run workflow"
3. Select branch: `main`
4. Check "Publish to TestPyPI instead of PyPI": `true`
5. Click "Run workflow"

The workflow will:
- Build the package
- Run tests on multiple platforms
- Publish to TestPyPI
- Test installation from TestPyPI

### Method 2: Manual Publication

```bash
# Build the package
python -m build

# Upload to TestPyPI
twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ \
            langquality
```

### Verify TestPyPI Installation

```bash
# Create a fresh virtual environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ \
            langquality

# Test the installation
langquality --help
langquality pack list
python -c "from langquality.language_packs.manager import LanguagePackManager; print('Success!')"

# Deactivate and remove test environment
deactivate
rm -rf test_env
```

## Publishing to PyPI

Once you've verified everything works on TestPyPI, you can publish to PyPI.

### Method 1: Using GitHub Release (Recommended)

1. **Update Version Number**
   - Update version in `setup.py` and `pyproject.toml`
   - Update `CHANGELOG.md` with release notes

2. **Commit and Push**
   ```bash
   git add setup.py pyproject.toml CHANGELOG.md
   git commit -m "Bump version to X.Y.Z"
   git push origin main
   ```

3. **Create a Git Tag**
   ```bash
   git tag -a vX.Y.Z -m "Release version X.Y.Z"
   git push origin vX.Y.Z
   ```

4. **Create GitHub Release**
   - Go to repository → Releases → "Draft a new release"
   - Choose the tag you just created
   - Release title: `vX.Y.Z`
   - Description: Copy relevant section from CHANGELOG.md
   - Click "Publish release"

5. **Automatic Publication**
   - The release workflow will automatically trigger
   - It will build, test, and publish to PyPI
   - Monitor the workflow in the Actions tab

### Method 2: Manual Publication (Not Recommended)

```bash
# Build the package
python -m build

# Upload to PyPI
twine upload dist/*

# Verify installation
pip install langquality
langquality --help
```

## Version Numbering

LangQuality follows [Semantic Versioning](https://semver.org/):

- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Pre-release Versions

For pre-releases, use:
- **Alpha**: `1.0.0a1`, `1.0.0a2`, ...
- **Beta**: `1.0.0b1`, `1.0.0b2`, ...
- **Release Candidate**: `1.0.0rc1`, `1.0.0rc2`, ...

## Release Checklist

Before each release, complete this checklist:

- [ ] All tests pass (`pytest tests/`)
- [ ] Code quality checks pass (`flake8`, `mypy`, `black --check`)
- [ ] Documentation is up to date
- [ ] CHANGELOG.md is updated with release notes
- [ ] Version number is updated in `setup.py` and `pyproject.toml`
- [ ] All language packs are validated
- [ ] Package builds successfully (`python -m build`)
- [ ] Package passes twine check (`twine check dist/*`)
- [ ] Package installs and works locally
- [ ] Package tested on TestPyPI
- [ ] Git tag created and pushed
- [ ] GitHub release created

## Troubleshooting

### Package Already Exists on PyPI

If you get an error that the package already exists:
- You cannot overwrite a version on PyPI
- Increment the version number and try again
- Use `--skip-existing` flag for TestPyPI

### Missing Dependencies

If users report missing dependencies:
- Check `install_requires` in `setup.py`
- Check `dependencies` in `pyproject.toml`
- Ensure all required packages are listed

### Language Packs Not Included

If language packs are missing from the distribution:
- Check `package_data` in `setup.py`
- Check `[tool.setuptools.package-data]` in `pyproject.toml`
- Verify `include_package_data = True` is set
- Check `MANIFEST.in` if it exists

### Import Errors After Installation

If users get import errors:
- Verify package structure with `python -m build`
- Check that `__init__.py` files exist in all packages
- Test installation in a clean virtual environment

## Post-Release Tasks

After a successful release:

1. **Announce the Release**
   - Post in GitHub Discussions
   - Update documentation website
   - Share on social media (if applicable)

2. **Monitor Issues**
   - Watch for installation issues
   - Respond to bug reports quickly
   - Prepare hotfix if critical bugs found

3. **Update Documentation**
   - Ensure ReadTheDocs builds successfully
   - Update any external documentation

4. **Plan Next Release**
   - Review open issues and PRs
   - Update roadmap
   - Plan features for next version

## Security Considerations

- **Never commit API tokens** to the repository
- Use **Trusted Publishers** (OIDC) instead of API tokens
- Enable **2FA** on PyPI and TestPyPI accounts
- Use **GitHub environment protection rules** for production releases
- **Review all code** before publishing (especially community contributions)

## Resources

- [PyPI Help](https://pypi.org/help/)
- [Python Packaging Guide](https://packaging.python.org/)
- [Trusted Publishers Guide](https://docs.pypi.org/trusted-publishers/)
- [Semantic Versioning](https://semver.org/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

## Support

If you encounter issues with publication:
1. Check the [GitHub Actions logs](https://github.com/langquality/langquality/actions)
2. Review this guide
3. Open an issue in the repository
4. Contact the maintainers
