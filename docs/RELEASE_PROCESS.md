# Release Process

Quick reference guide for releasing new versions of LangQuality.

## Quick Release Checklist

- [ ] Update CHANGELOG.md with release notes
- [ ] Run `python scripts/prepare_release.py --version X.Y.Z`
- [ ] Review and commit changes
- [ ] Create and push git tag
- [ ] Create GitHub release
- [ ] Verify automatic PyPI publication

## Detailed Steps

### 1. Prepare the Release

```bash
# Update CHANGELOG.md with release notes
vim CHANGELOG.md

# Run the release preparation script
python scripts/prepare_release.py --version 1.0.0

# Review changes
git diff

# Commit version bump
git add setup.py pyproject.toml CHANGELOG.md
git commit -m "Bump version to 1.0.0"
git push origin main
```

### 2. Create Git Tag

```bash
# Create annotated tag
git tag -a v1.0.0 -m "Release version 1.0.0"

# Push tag
git push origin v1.0.0
```

### 3. Create GitHub Release

1. Go to https://github.com/langquality/langquality-toolkit/releases/new
2. Select tag: `v1.0.0`
3. Release title: `v1.0.0`
4. Description: Copy relevant section from CHANGELOG.md
5. Click "Publish release"

### 4. Automatic Publication

The GitHub Actions workflow will automatically:
- Build the package
- Test on multiple platforms
- Publish to PyPI
- Update release notes

Monitor progress at: https://github.com/langquality/langquality-toolkit/actions

### 5. Verify Publication

```bash
# Wait a few minutes for PyPI to update
sleep 120

# Install from PyPI
pip install --upgrade langquality

# Test installation
langquality --version
langquality --help
```

## Testing on TestPyPI First

Before publishing to PyPI, test on TestPyPI:

1. Go to Actions → Release workflow
2. Click "Run workflow"
3. Check "Publish to TestPyPI"
4. Click "Run workflow"

Then test installation:

```bash
pip install --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ \
            langquality
```

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0): Breaking changes
- **MINOR** (1.X.0): New features (backward compatible)
- **PATCH** (1.0.X): Bug fixes (backward compatible)

### Pre-release Versions

- **Alpha**: `1.0.0a1` - Early testing
- **Beta**: `1.0.0b1` - Feature complete, testing
- **RC**: `1.0.0rc1` - Release candidate

## Hotfix Process

For urgent bug fixes:

```bash
# Create hotfix branch from tag
git checkout -b hotfix/1.0.1 v1.0.0

# Make fixes
git commit -m "Fix critical bug"

# Update version to 1.0.1
python scripts/prepare_release.py --version 1.0.1

# Merge to main
git checkout main
git merge hotfix/1.0.1

# Tag and release
git tag -a v1.0.1 -m "Hotfix release 1.0.1"
git push origin main v1.0.1
```

## Rollback Process

If a release has critical issues:

1. **Yank the release on PyPI** (doesn't delete, but prevents new installs)
   - Go to https://pypi.org/project/langquality/
   - Click on the problematic version
   - Click "Options" → "Yank release"

2. **Create a hotfix release** with the fix

3. **Update documentation** to warn about the yanked version

## Common Issues

### Build Fails

```bash
# Clean build artifacts
rm -rf dist/ build/ *.egg-info

# Rebuild
python -m build
```

### Tests Fail

```bash
# Run tests locally
pytest tests/ -v

# Fix issues and commit
git add .
git commit -m "Fix failing tests"
```

### PyPI Upload Fails

- Check that version doesn't already exist on PyPI
- Verify GitHub environment secrets are configured
- Check GitHub Actions logs for details

## Resources

- [Full PyPI Publication Guide](./PYPI_PUBLICATION_GUIDE.md)
- [CHANGELOG.md](../CHANGELOG.md)
- [Semantic Versioning](https://semver.org/)
- [GitHub Releases](https://github.com/langquality/langquality-toolkit/releases)
