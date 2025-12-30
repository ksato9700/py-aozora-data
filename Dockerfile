FROM python:3.13-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
# --frozen: use uv.lock
# --no-dev: exclude dev dependencies
RUN uv sync --frozen --no-dev

# Copy source code
COPY aozora_data ./aozora_data

# Set environment variables
# Ensure python (and scripts) installed by uv are in PATH.
# uv installs into .venv by default.
ENV PATH="/app/.venv/bin:$PATH"

# Entrypoint
CMD ["python", "-m", "aozora_data.importer.main"]
