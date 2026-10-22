FROM python:3.13-slim

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml granian.toml ./
COPY src/ ./src/

# Install dependencies
RUN pip install --no-cache-dir -e ".[dev]"

# Expose port
EXPOSE 8000

# Run with Granian + uvloop
CMD ["granian", "--interface", "asgi", "--config", "granian.toml", "app.main:app"]
