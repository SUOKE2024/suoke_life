# Look Service Makefile

.PHONY: help install install-dev test test-cov lint format clean run

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  lint         - Run linting"
	@echo "  format       - Format code"
	@echo "  clean        - Clean up generated files"
	@echo "  run          - Run the service"
	@echo "  run-dev      - Run development server"

# Installation
install:
	uv sync --no-dev

install-dev:
	uv sync

# Testing
test:
	uv run pytest

test-cov:
	uv run pytest --cov=look_service --cov-report=html --cov-report=term-missing

test-unit:
	uv run pytest tests/unit/

test-integration:
	uv run pytest tests/integration/

# Code quality
lint:
	uv run ruff check .
	uv run mypy look_service tests

format:
	uv run ruff format .
	uv run ruff check --fix .

# Development
run:
	uv run python -m look_service.cmd.server

run-dev:
	uv run uvicorn look_service.api.app:create_app --factory --reload --host 0.0.0.0 --port 8080

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/

# Monitoring
health:
	curl http://localhost:8080/health

# Security check (optional)
security-check:
	@echo "Running security checks..."
	@if command -v safety >/dev/null 2>&1; then \
		uv run safety check; \
	else \
		echo "Safety not installed, skipping security check"; \
	fi

# Environment
env-copy:
	cp env.example .env

# Check all (without security check for now)
check-all: lint test
	@echo "All checks completed successfully!" 