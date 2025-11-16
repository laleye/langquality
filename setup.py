"""Setup script for LangQuality - Language Quality Toolkit."""

from setuptools import setup, find_packages
from pathlib import Path

# Read long description from README
readme_file = Path(__file__).parent / "README.md"
with open(readme_file, "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read core requirements
requirements_file = Path(__file__).parent / "requirements.txt"
with open(requirements_file, "r", encoding="utf-8") as fh:
    requirements = [
        line.strip() 
        for line in fh 
        if line.strip() and not line.startswith("#") and not line.startswith("pytest")
    ]

# Define optional dependencies
extras_require = {
    # Development dependencies
    "dev": [
        "pytest>=7.3.0",
        "pytest-cov>=4.1.0",
        "pytest-xdist>=3.3.0",
        "pytest-benchmark>=4.0.0",
        "pytest-mock>=3.11.0",
        "black>=23.12.0",
        "isort>=5.13.0",
        "flake8>=7.0.0",
        "flake8-docstrings>=1.7.0",
        "flake8-bugbear>=23.12.0",
        "mypy>=1.8.0",
        "types-PyYAML>=6.0.0",
        "bandit>=1.7.6",
        "pre-commit>=3.6.0",
        "ipython>=8.12.0",
        "ipdb>=0.13.13",
    ],
    # Documentation dependencies
    "docs": [
        "sphinx>=7.2.0",
        "sphinx-rtd-theme>=2.0.0",
        "myst-parser>=2.0.0",
        "sphinx-autodoc-typehints>=1.25.0",
        "mkdocs>=1.5.0",
        "mkdocs-material>=9.5.0",
    ],
    # Build and packaging dependencies
    "build": [
        "build>=1.0.0",
        "twine>=4.0.0",
        "setuptools>=68.0.0",
        "wheel>=0.42.0",
    ],
    # NLP optional dependencies (for specific tokenizers)
    "spacy": [
        "spacy>=3.5.0",
    ],
    "nltk": [
        "nltk>=3.8",
    ],
}

# Add 'all' extra that includes all optional dependencies
extras_require["all"] = list(set(
    dep for extra_deps in extras_require.values() for dep in extra_deps
))

setup(
    name="langquality",
    version="1.0.0",
    author="LangQuality Community",
    author_email="community@langquality.org",
    maintainer="LangQuality Community",
    maintainer_email="community@langquality.org",
    description="Language Quality Toolkit for Low-Resource Languages",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/langquality/langquality",
    project_urls={
        "Homepage": "https://github.com/langquality/langquality",
        "Documentation": "https://langquality.readthedocs.io",
        "Repository": "https://github.com/langquality/langquality",
        "Bug Tracker": "https://github.com/langquality/langquality/issues",
        "Changelog": "https://github.com/langquality/langquality/blob/main/CHANGELOG.md",
        "Discussions": "https://github.com/langquality/langquality/discussions",
    },
    license="MIT",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3 :: Only",
        "Natural Language :: English",
        "Natural Language :: French",
    ],
    keywords=[
        "nlp",
        "low-resource-languages",
        "data-quality",
        "linguistics",
        "language-packs",
        "text-analysis",
        "dataset-quality",
        "multilingual",
        "language-toolkit",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require=extras_require,
    entry_points={
        "console_scripts": [
            "langquality=langquality.__main__:main",
            "fongbe-quality=fongbe_quality.__main__:main",  # Deprecated, for backward compatibility
        ],
    },
    include_package_data=True,
    package_data={
        "langquality": [
            "resources/*",
            "outputs/templates/*",
            "language_packs/packs/*/config.yaml",
            "language_packs/packs/*/metadata.json",
            "language_packs/packs/*/resources/*",
            "language_packs/packs/*/README.md",
            "language_packs/packs/_template/**/*",
        ],
        "fongbe_quality": [
            "resources/*",
            "outputs/templates/*",
        ],
    },
    zip_safe=False,
)
