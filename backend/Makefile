.PHONY: install dev run granian test lint format clean docker-build docker-up

# Install dependencies
install:
	pip install -e "."

install-dev:
	pip install -e ".[dev]"

# Development
dev:
	python -m app.main

# Production with Granian
granian:
	granian --interface asgi --config granian.toml app.main:app

# Testing
test:
	pytest tests/ -v --asyncio-mode=auto

test-cov:
	pytest tests/ -v --asyncio-mode=auto --cov=src/app --cov-report=term-missing

# Linting
lint:
	ruff check src/ tests/
	mypy src/

format:
	ruff format src/ tests/
	ruff check --fix src/ tests/

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
	prefect server start

prefect-flow:
	python -c "from app.infrastructure.prefect_flows import data_pipeline_flow; import asyncio; asyncio.run(data_pipeline_flow())"
