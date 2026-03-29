# Simplified production image for PotionLab API
# NOTE: This version uses host .venv due to Docker network restrictions in dev environment
# For production with network access, use multi-stage build with `uv sync` inside container

FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 && rm -rf /var/lib/apt/lists/* || true

# Copy application source code
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY pyproject.toml ./

# Install uv and sync dependencies using system Python
# This works because we're using the slim image which matches the dev Python version
RUN pip install uv --break-system-packages && uv sync --no-dev --system

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

# Run uvicorn server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
