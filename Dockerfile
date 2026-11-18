# syntax=docker/dockerfile:1

# =============================================================================
# Builder Stage: Install dependencies and build the package
# =============================================================================
FROM python:3.11-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.11.24 /uv /usr/local/bin/uv

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_PYTHON_DOWNLOADS=never

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /build

# Cache locked dependencies separately from the source code.
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --extra mcp --no-install-project

COPY README.md ./
COPY src/ ./src/
RUN uv sync --locked --no-dev --extra mcp --no-editable

# =============================================================================
# Runtime Stage: Slim production image
# =============================================================================
FROM python:3.11-slim AS runtime

# Metadata labels
LABEL maintainer="Matthew G. Monteleone <matthewm@augmentcode.com>" \
      description="DevRev MCP Server - A Model Context Protocol server for the DevRev platform" \
      version="2.6.0" \
      org.opencontainers.image.source="https://github.com/mgmonteleone/py-dev-rev" \
      org.opencontainers.image.title="DevRev MCP Server" \
      org.opencontainers.image.description="Production-ready MCP server for DevRev API integration" \
      org.opencontainers.image.version="2.6.0" \
      org.opencontainers.image.licenses="MIT"

# Set environment variables for Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:/home/mcp/.local/bin:$PATH"

# Install runtime dependencies (curl for healthcheck)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash mcp && \
    mkdir -p /app && \
    chown -R mcp:mcp /app

# Set working directory
WORKDIR /app

COPY --from=builder /opt/venv /opt/venv

# Switch to non-root user
USER mcp

# Expose the HTTP port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Set the entry point
ENTRYPOINT ["devrev-mcp-server"]

# Default command arguments
CMD ["--transport", "streamable-http", "--host", "0.0.0.0", "--port", "8080"]

