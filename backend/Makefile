.PHONY: install dev granian test lint format clean docker-build docker-up

# Install (uv)
install:
	uv sync

install-dev:
	uv sync --dev

# Development
dev:
	uv run python -m app.main

# Production with Granian
granian:
	uv run granian --interface asgi --config granian.toml app.main:app

# Testing
test:
	uv run pytest tests/ -v --asyncio-mode=auto

test-cov:
	uv run pytest tests/ -v --asyncio-mode=auto --cov=src/app --cov-report=term-missing

# Linting
lint:
	uv run ruff check src/ tests/
	uv run mypy src/

format:
	uv run ruff format src/ tests/
	uv run ruff check --fix src/ tests/

# Clean
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .mypy_cache .pytest_cache .ruff_cache dist/ build/ *.egg-info

# Docker
docker-build:
	docker build -t async-poc .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

# Prefect (optional)
prefect-server:
	uv run prefect server start
