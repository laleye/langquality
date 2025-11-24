# Known Test Issues

This document tracks tests that are currently marked as `xfail` (expected to fail) in the test suite.

## Why are these tests marked as xfail?

These tests expose existing bugs or issues in the codebase that need to be fixed. They are marked as `xfail` to allow CI/CD pipelines to pass while we work on fixing the underlying issues.

## List of Known Issues

### Error Handling Tests (5 tests)
- `test_invalid_csv_missing_columns` - CSV validation not properly rejecting missing columns
- `test_csv_with_encoding_issues` - CSV loader including header row in results
- `test_pipeline_all_analyzers_fail` - Error message format mismatch
- `test_csv_with_empty_french_column` - Empty row filtering not working correctly
- `test_pipeline_with_very_large_sentences` - Large sentences not being flagged as too long

### Analyzer Registry Tests (3 tests)
- `test_register_invalid_interface` - Interface validation not raising expected errors
- `test_validate_missing_methods` - Method validation returning incorrect results
- `test_validate_missing_properties` - Property validation returning incorrect results

### Domain Analyzer Tests (1 test)
- `test_identify_underrepresented_domains` - Underrepresented domain detection logic issue

### Gender Bias Analyzer Tests (6 tests)
- `test_analyze_basic` - Missing required `config` parameter in test
- `test_count_gender_mentions` - Missing required `config` parameter in test
- `test_compute_gender_ratio` - Missing required `config` parameter in test
- `test_compute_gender_ratio_zero_masculine` - Missing required `config` parameter in test
- `test_detect_stereotypes` - Missing required `config` parameter in test
- `test_gender_bias_analyzer_with_pack` - KeyError: 'patterns' in stereotype detection

### Data Loader Tests (3 tests)
- `test_load_csv_basic` - CSV loader including header row in results
- `test_load_csv_skip_empty_rows` - CSV loader including header row in results
- `test_load_directory` - CSV loader including header row in results

### Exporter Tests (1 test)
- `test_create_execution_log` - Log header text mismatch (expects "FONGBE" but gets "LANGQUALITY")

## How to Fix

To fix these issues and remove the xfail markers:

1. Fix the underlying bug in the source code
2. Verify the test passes locally
3. Remove the test from the `known_failing_tests` list in `tests/conftest.py`
4. Update this document

## Configuration

The xfail markers are automatically applied in `tests/conftest.py` using the `pytest_collection_modifyitems` hook.
