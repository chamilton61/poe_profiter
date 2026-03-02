FROM python:3.11-slim AS base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy dependency files and install Python dependencies
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy application code
COPY app/ ./app/

# Expose port
EXPOSE 8000

# Run the application
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
<<<<<<< HEAD


FROM base AS test

# Install dev dependencies (adds pytest, httpx)
RUN uv sync --frozen

# Copy test files
COPY tests/ ./tests/

CMD ["uv", "run", "pytest", "tests/", "-v"]
=======
>>>>>>> d763244 (removed requirements and added manager)
