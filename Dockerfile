# Multi-stage production image for PotionLab API
# Stage 1: Builder - Install dependencies and create virtual environment
# Stage 2: Runtime - Minimal runtime with only necessary artifacts

# ============================================================================
# STAGE 1: Builder
# ============================================================================
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build tools (uv for dependency management)
RUN pip install uv --break-system-packages

# Copy dependency files
COPY pyproject.toml ./

# Sync dependencies into a clean virtual environment
# --no-dev excludes development dependencies for production
RUN uv sync --no-dev --system

# ============================================================================
# STAGE 2: Runtime
# ============================================================================
FROM python:3.12-slim

WORKDIR /app

# Install only runtime dependencies (PostgreSQL client library)
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 && rm -rf /var/lib/apt/lists/* || true

# Copy virtual environment from builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy application source code
COPY src/ ./src/
COPY scripts/ ./scripts/

# Set Python path to use the copied virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

# Run uvicorn server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
