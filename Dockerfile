# ============================================================================
# Brain-5D — Dockerfile
# ============================================================================
# Multi-stage build for minimal production image.
#
# Build:    docker build -t brain5d .
# Run:      docker run --rm -p 8765:8765 brain5d
# Run with: docker run --rm -v ./configs:/app/configs brain5d \
#             python -m src.main --config configs/poc_config.yaml
# ============================================================================

# ---- Build stage -----------------------------------------------------------
FROM python:3.13-slim AS builder

WORKDIR /build

# Install build dependencies
RUN pip install --no-cache-dir build "setuptools>=68" wheel

# Copy package metadata and sources
COPY pyproject.toml setup.py README.md ./
COPY src/ src/

# Build wheel
RUN python -m build --wheel --no-isolation

# ---- Runtime stage ---------------------------------------------------------
FROM python:3.13-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy built wheel from builder
COPY --from=builder /build/dist/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm /tmp/*.whl

# Copy source code (for editable imports)
COPY src/ src/
COPY configs/ configs/
COPY scripts/ scripts/

# Expose dashboard port
EXPOSE 8765

# Default: show help
CMD ["python", "-m", "src.main", "--help"]
