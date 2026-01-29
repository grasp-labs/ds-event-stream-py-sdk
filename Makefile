# 📦 DS Shared Python Package Makefile
#
# Structured Makefile for building, testing, documenting, and publishing the package.

# ===== Configuration =====

# Python/package configuration
SRC_DIR         ?= src
TEST_DIR        ?= tests
DOCS_DIR        ?= docs
MODULE_NAME     ?= ds_event_stream_py_sdk

# Colors for terminal output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

# ===== Help =====

.PHONY: help
help: ## Show this help message
	@echo "$(BLUE)DS Shared Logger - Development Commands$(NC)"
	@echo ""
	@echo "$(GREEN)Available commands:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# ===== Housekeeping =====

.PHONY: clean
clean: ## Clean build and cache artifacts
	rm -rf build/ dist/ *.egg-info/ .pytest_cache/ .coverage htmlcov/ .mypy_cache/ .ruff_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

# ===== Code Quality =====

.PHONY: lint
lint: ## Lint with ruff
	uv run ruff check --config .config/ruff.toml --fix --exit-non-zero-on-fix $(SRC_DIR) $(TEST_DIR)
	uv run pre-commit run markdownlint --all-files

.PHONY: format
format: ## Format with ruff
	uv run ruff format --config .config/ruff.toml .

.PHONY: type-check
type-check: ## Type-check with mypy
	uv run mypy --config-file .config/mypy.ini $(SRC_DIR)

.PHONY: security-check
security-check: ## Run security checks (bandit)
	uv run bandit -r $(SRC_DIR) || true

# ===== Tests =====

.PHONY: test
test: ## Run tests
	uv run pytest -c .config/pytest.ini $(TEST_DIR) -v

.PHONY: test-cov
test-cov: ## Run tests with coverage (html + xml)
	uv run pytest -c .config/pytest.ini $(TEST_DIR) --cov=$(MODULE_NAME) --cov-report=term-missing --cov-report=html --cov-report=xml --cov-config=.config/coverage.ini

# ===== Build & Publish =====

.PHONY: build
build: clean ## Build the package
	uv build

.PHONY: publish-test
publish-test: build ## Upload to TestPyPI
	@echo "Uploading to TestPyPI..."
	uv run twine upload --repository testpypi dist/* --verbose

.PHONY: publish
publish: build ## Upload to PyPI
	@echo "Uploading to PyPI..."
	uv run twine upload dist/* --verbose

# ===== Docs =====

.PHONY: docs
docs: ## Build Sphinx documentation
	uv run sphinx-build -b html $(DOCS_DIR)/source $(DOCS_DIR)/build/html

# ===== Versioning =====

PYPROJECT_VERSION := $(shell python -c "import pathlib,re; t=pathlib.Path('pyproject.toml').read_text(encoding='utf-8'); m=re.search(r'(?ms)^\\[project\\]\\s.*?^version\\s*=\\s*\"([^\"]+)\"', t); print(m.group(1) if m else '')")

.PHONY: version
version: ## Show current version
	@echo "$(PYPROJECT_VERSION)"

.PHONY: tag
tag: ## Tag the current version from pyproject.toml and push to origin (triggers release)
	@test -n "$(PYPROJECT_VERSION)" || (echo "❌ Could not read version from pyproject.toml" && exit 1)
	@git tag -a "v$(PYPROJECT_VERSION)" -m "Version v$(PYPROJECT_VERSION)"
	@git push origin "v$(PYPROJECT_VERSION)"

# ===== End of Makefile =====
