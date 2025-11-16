# Makefile for LangQuality development tasks

.PHONY: help install install-dev test test-cov lint format type-check clean pre-commit docs build

help:
	@echo "LangQuality Development Commands:"
	@echo "  make install        Install package in development mode"
	@echo "  make install-dev    Install package with development dependencies"
	@echo "  make test           Run tests"
	@echo "  make test-cov       Run tests with coverage report"
	@echo "  make lint           Run linting checks"
	@echo "  make format         Format code with black and isort"
	@echo "  make type-check     Run type checking with mypy"
	@echo "  make pre-commit     Install and run pre-commit hooks"
	@echo "  make clean          Clean build artifacts"
	@echo "  make docs           Build documentation"
	@echo "  make build          Build distribution packages"

install:
	pip install -e .

install-dev:
	pip install -e .
	pip install -r requirements-dev.txt
	pre-commit install

test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=langquality --cov=fongbe_quality --cov-report=term-missing --cov-report=html

lint:
	@echo "Running flake8..."
	flake8 src/ tests/
	@echo "Running isort check..."
	isort --check-only src/ tests/
	@echo "Running black check..."
	black --check src/ tests/

format:
	@echo "Formatting with isort..."
	isort src/ tests/
	@echo "Formatting with black..."
	black src/ tests/

type-check:
	mypy src/langquality --ignore-missing-imports --no-strict-optional

pre-commit:
	pre-commit install
	pre-commit run --all-files

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

docs:
	cd docs && make html

build:
	python -m build

.DEFAULT_GOAL := help
