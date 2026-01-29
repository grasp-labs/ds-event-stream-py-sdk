# Contributing Guidelines

Thank you for your interest in contributing! This document provides guidelines
and standards for contributing to DS Python Library packages.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Follow the project's coding standards

## Getting Started

1. **Fork the repository** (if contributing to an existing package)
2. **Clone your fork**:

   ```bash
   git clone https://github.com/grasp-labs/ds-event-stream-py-sdk.git
   cd ds-event-stream-py-sdk
   ```

3. **Set up development environment**:

   ```bash
   uv sync --all-extras --dev
   uv run pre-commit install
   ```

4. **Create a branch** for your changes:

   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Before You Start

1. Check existing issues and pull requests to avoid duplicate work
2. Create an issue to discuss major changes before implementing
3. Ensure you can build and test the project: `make test`

### Making Changes

1. **Write code** following the project standards (see below)
2. **Run quality checks**:

   ```bash
   make lint          # Check code quality
   make format        # Format code
   make type-check    # Type checking
   make test-cov      # Run tests with coverage
   ```

3. **Ensure all checks pass** before submitting

### Submitting Changes

1. **Commit your changes** with clear, descriptive commit messages:

   ```bash
   git commit -m "Add feature: description of what was added"
   ```

2. **Push to your fork**:

   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create a Pull Request** with:
   - Clear description of changes
   - Reference to related issues
   - Screenshots/examples if applicable

## Coding Standards

### Code Style

- **Follow PEP 8** coding standards
- **Use type hints** for all functions and methods
- **Line length**: 131 characters (as configured in Ruff)
- **Format code** using Ruff before committing

### Documentation

All code must be properly documented:

#### File-Level Documentation

Every Python file must begin with:

```python
"""
File: <filename>.py
Description: <brief description of the file's responsibility>
Region: <packages/aws|packages/logging|packages/messaging|packages/shared>

# Example:

# Usage example here
"""
```

#### Function-Level Documentation

All functions must include docstrings:

```python
def example_function(param1: int, param2: str) -> bool:
    """
    Short description of the function.

    Args:
        param1: Description of the first parameter.
        param2: Description of the second parameter.

    Returns:
        Description of the return value.

    Example:
        >>> example_function(1, "test")
        True
    """
```

### Code Quality Rules

- **Functions must be small** and serve a single purpose
- **Avoid deeply nested logic**; use early returns when possible
- **Group constants** at the top of the file
- **Use explicit logic**; avoid magic patterns
- **Favor composition** over inheritance
- **Include clear error messages** in exceptions

### Naming Conventions

- **Functions and variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_CASE`
- **Use f-strings** for string formatting

### Type Hints

Type hints are **mandatory** for all functions:

```python
def process_data(data: list[str], threshold: float = 0.5) -> dict[str, int]:
    """Process data and return results."""
    # Implementation
```

## Testing Requirements

### Test Coverage

- **Minimum coverage**: 95%
- All new code must include tests
- Tests must pass before submitting PR

### Writing Tests

```python
"""
File: test_example.py
Description: Tests for example module
"""

import pytest
from ds_event_stream_py_sdk.example import example_function


def test_example_function_basic() -> None:
    """Test basic functionality of example_function."""
    result = example_function(1, "test")
    assert result is True


def test_example_function_edge_cases() -> None:
    """Test edge cases."""
    # Test implementation
```

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
uv run pytest tests/test_example.py -v
```

## Pre-commit Hooks

Pre-commit hooks automatically check code quality:

```bash
# Install hooks (one-time setup)
uv run pre-commit install

# Run hooks manually
uv run pre-commit run --all-files
```

Hooks check for:

- Trailing whitespace
- End of file formatting
- YAML/TOML/JSON validity
- Code formatting (Ruff)
- Type checking (mypy)
- Docstring requirements

## Pull Request Process

### PR Requirements

1. **All tests pass**: `make test-cov`
2. **Code is formatted**: `make format`
3. **Type checking passes**: `make type-check`
4. **Linting passes**: `make lint`
5. **Coverage maintained**: At least 95%
6. **Documentation updated**: If adding features

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe how you tested your changes

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] Coverage maintained (95%+)
```

## Version Management

Version bumps follow [Semantic Versioning](https://semver.org/):

- **Patch** (0.1.0 → 0.1.1): Bug fixes
- **Minor** (0.1.0 → 0.2.0): New features (backward compatible)
- **Major** (0.1.0 → 1.0.0): Breaking changes

Only maintainers bump versions.

## Prohibited Practices

Do **not**:

- Include unused imports, variables, or placeholder code
- Use `pass` blocks or TODO comments
- Hardcode values (use configuration)
- Modify CI/CD files without permission
- Create test files unless explicitly needed
- Break existing functionality without discussion

## Getting Help

If you need help:

1. Check existing documentation
2. Review similar code in the repository
3. Ask questions in issues or discussions
4. Reach out to maintainers

## Recognition

Contributors will be recognized in:

- GitHub Release notes
- Project documentation (if applicable)

Thank you for contributing!
