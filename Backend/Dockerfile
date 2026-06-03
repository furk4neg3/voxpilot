# VoxPilot - TTS / Voice AI Studio PoC
FROM python:3.11-slim AS base

# System dependencies.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python dependencies. ML dependencies are optional to keep default builds
# small and CI/demo-friendly. pip is only used to bootstrap uv.
ARG INSTALL_ML=true
COPY requirements.txt requirements-ml.txt ./
RUN pip install --no-cache-dir uv && \
    uv pip install --system --no-cache -r requirements.txt && \
    if [ "$INSTALL_ML" = "true" ]; then \
      uv pip install --system --no-cache torch --index-url https://download.pytorch.org/whl/cpu && \
      uv pip install --system --no-cache -r requirements-ml.txt; \
    fi

# Application code
COPY . .

# Create data directories
RUN mkdir -p data/generated

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the API server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
