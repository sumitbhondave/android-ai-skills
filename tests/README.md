# Maintenance & Testing Guide

This directory contains the tools and scripts used to ensure the stability and security of the
`ai-skills` library.

## Test Suite

The primary test suite is located at `tests/test_suite.py`. It verifies:

1. **Installer Logic**: Ensures the installation process doesn't crash and handles dry-runs
   correctly.
2. **Integrity Logic**: Verifies that the SHA-256 hashing correctly detects file modifications.
3. **Scaffolding**: Checks that the new-skill generator is functionally sound.

### Running Tests

To run the developer tests, use:

```bash
python3 tests/test_suite.py
```

## CI/CD Integration

All tests are automatically run on every Push or Pull Request via GitHub Actions
(`.github/workflows/validate.yml`). The CI pipeline includes:

- **Python Compilation**: Checks for syntax errors in all `.py` files.
- **Checksum Verification**: Ensures `CHECKSUMS.txt` is up-to-date.
- **Schema Validation**: Ensures every skill has a valid `skill.json`.
