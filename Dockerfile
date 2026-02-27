# Build stage
FROM python:3.13-alpine3.21 AS builder

# Environment variables configuration for optimization
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/code

# Working directory configuration
WORKDIR /code

# Installation of build dependencies (Alpine uses apk instead of apt-get)
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    openssl-dev \
    cargo \
    jpeg-dev \
    zlib-dev \
    libjpeg

# CodeArtifact pip index URL (passed as build arg)
ARG PIP_INDEX_URL
ENV PIP_INDEX_URL=${PIP_INDEX_URL}

# Copy and installation of dependencies
COPY requirements.txt /code/
RUN pip install --no-cache-dir --upgrade pip && \
    grep -v "pytest\|matplotlib\|numpy\|statistics" requirements.txt > requirements-prod.txt && \
    pip install --no-cache-dir -r requirements-prod.txt && \
    find /usr/local -name '*.pyc' -delete && \
    find /usr/local -name '__pycache__' -delete && \
    # Clean build dependencies
    apk del .build-deps

# Final stage
FROM python:3.13-alpine3.21 AS final

# Image metadata
LABEL maintainer="FastAPI Counter HREF <alvarolinarescabre@gmail.com>" \
      description="FastAPI application for counting href tags in web content" \
      version="1.0"

# Environment variables for execution
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=80 \
    CACHE_DB_PATH=/app/cache/sqlite_cache.db

# Create non-root user for security (Alpine uses addgroup/adduser instead of groupadd/useradd)
RUN addgroup -S appuser && adduser -S -G appuser appuser

# Create cache directory with proper permissions
RUN mkdir -p /app/cache && chown -R appuser:appuser /app/cache

# Install curl for healthcheck and necessary runtime dependencies
RUN apk add --no-cache curl tzdata ca-certificates

# Working directory configuration
WORKDIR /app

# Copy dependencies installed from the builder
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy source code
COPY --chown=appuser:appuser . /app/

# Set proper permissions for application directories
RUN chown -R appuser:appuser /app

# Application port
EXPOSE 80

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/healthcheck || exit 1

# Switch to non-root user
USER appuser

# Command to start the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
