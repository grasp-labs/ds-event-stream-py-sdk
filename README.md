# ds-event-stream-py-sdk

![Python Versions](https://img.shields.io/badge/python-3.10%20|%203.11%20|%203.12%20|%203.13-blue)
[![PyPI version](https://badge.fury.io/py/ds-event-stream-py-sdk.svg?kill_cache=1)](https://badge.fury.io/py/ds-event-stream-py-sdk)
[![Build Status](https://github.com/grasp-labs/ds-event-stream-py-sdk/actions/workflows/build.yaml/badge.svg)](https://github.com/grasp-labs/ds-event-stream-py-sdk/actions/workflows/build.yaml)
[![codecov](https://codecov.io/gh/grasp-labs/ds-event-stream-py-sdk/graph/badge.svg?token=EO3YCNCZFS)](https://codecov.io/gh/grasp-labs/ds-event-stream-py-sdk)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

DS package for ds-event-stream-py-sdk

## Quick Start

### Quick Setup

```shell
# 3. Install dependencies
uv sync --all-extras --dev

# 4. Install pre-commit hooks
uv run pre-commit install

# 5. Verify setup
make test
```

## Development

### Available Commands

Use the Makefile for all development tasks:

```shell
# Show all available commands
make help

# Code Quality
make lint           # Check code quality with ruff
make format         # Format code with ruff
make type-check     # Run mypy type checking
make security-check # Run security checks with bandit

# Testing
make test          # Run tests
make test-cov      # Run tests with coverage (requires 95%)

# Build and Publish
make build         # Build package
make docs          # Build documentation
make publish-test  # Upload to TestPyPI
make publish       # Upload to PyPI
```

### Version Management

```shell
# Show current version
make version

# Tag and release
make tag           # Create git tag and push (triggers release)
```

> **⚠️ Warning**: The `make tag` command will create a git tag and
> push it to the remote repository, which may trigger automated
> releases. Ensure you have updated `pyproject.toml` with the new version
> and committed all changes before running this command.

### Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality:

```shell
install pre-commit
```

### Building Documentation

```shell
# Build documentation
make docs

# View documentation (macOS)
open docs/build/html/index.html

# View documentation (Linux)
xdg-open docs/build/html/index.html
```

### Testing

```shell
# Run basic tests
make test

# Run tests with coverage (requires 95% coverage)
make test-cov

# Run specific test file
uv run pytest tests/test_example.py -v
```

## Project Structure

```text
.
├── .config/                   # Configuration tooling files
├── .github/
│   ├── workflows/            # CI/CD workflows
│   └── CODEOWNERS            # Code ownership file
├── src/
│   └── ds_common_{name}_py_lib/     # Rename to your module name
│       └── __init__.py
├── .pre-commit-config.yaml   # Pre-commit hooks configuration
├── tests/                    # Test files
├── docs/                     # Sphinx documentation
├── LICENSE-APACHE            # License file
├── pyproject.toml            # Project configuration
├── Makefile                  # Development commands
├── VERSION.txt               # Version file
├── codecov.yaml              # Codecov configuration
├── CONTRIBUTING.md           # Contribution guidelines
├── PyPI.md                   # PyPI publishing guide
├── README.md                 # This file
```

## Features

- **Modern Python Tooling**: Uses `uv` for fast dependency management
- **Type Safety**: Strict mypy configuration with full type hints
- **Code Quality**: Ruff for linting and formatting
- **Testing**: Pytest with 95% coverage requirement
- **Documentation**: Sphinx with autoapi for automatic API docs
- **CI/CD**: GitHub Actions for testing, building, and publishing
- **Pre-commit Hooks**: Automated code quality checks
- **Docker Support**: Containerized build environment

## Requirements

- Python 3.9+
- [uv](https://github.com/astral-sh/uv) package manager
- Make (for development commands)

## Documentation

- [CONTRIBUTING.md](CONTRIBUTING.md) - Contribution guidelines
- [PyPI.md](PyPI.md) - PyPI publishing guide
- [README.md](README.md) - This file

## License

This package is licensed under the Apache License 2.0.
See [LICENSE-APACHE](LICENSE-APACHE) for details.
