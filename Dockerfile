FROM python:3.14-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock* granian.toml ./
COPY src/ ./src/

# Install dependencies with uv
RUN uv sync --frozen --no-dev

# Expose port
EXPOSE 8000

# Run with Granian + uvloop
CMD ["uv", "run", "granian", "--interface", "asgi", "--config", "granian.toml", "app.main:app"]
