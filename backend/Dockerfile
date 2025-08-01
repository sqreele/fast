# Build stage
FROM python:3.12-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies with error handling
RUN set -ex && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        postgresql-client \
        gcc \
        libc6-dev \
        libpq-dev \
        python3-dev \
        build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /var/cache/apt/*

# Development stage
FROM base AS development

# Install development dependencies
RUN set -ex && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        vim && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /var/cache/apt/*

# Create non-root user for development
RUN groupadd -g 1000 appuser && \
    useradd -u 1000 -g appuser -m -s /bin/bash appuser

# Copy requirements and install Python dependencies with better error handling
COPY requirements.txt requirements-dev.txt ./
RUN set -ex && \
    python -m pip install --upgrade pip setuptools wheel && \
    python -m pip install --no-cache-dir --timeout=300 -r requirements.txt && \
    python -m pip install --no-cache-dir --timeout=300 -r requirements-dev.txt

# Create necessary directories
RUN mkdir -p uploads/{images,documents,videos,audio,temp} tmp && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Default command for development
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Dependencies stage for production - simplified to avoid buildx issues
FROM base AS deps

# Copy requirements and install Python dependencies with retry logic
COPY requirements.txt ./
RUN set -ex && \
    for i in 1 2 3; do \
        python -m pip install --upgrade pip setuptools wheel && \
        python -m pip install --no-cache-dir --timeout=300 -r requirements.txt && \
        break || [ $i -eq 3 ] && exit 1 || sleep 10; \
    done

# Production stage
FROM python:3.12-slim AS production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

WORKDIR /app

# Install only runtime system dependencies
RUN set -ex && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        postgresql-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /var/cache/apt/*

# Copy installed packages from deps stage
COPY --from=deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Create necessary directories
RUN mkdir -p uploads/{images,documents,videos,audio,temp} tmp logs && \
    chown -R appuser:appuser /app

# Copy application code
COPY --chown=appuser:appuser . .

# Remove development files
RUN rm -rf requirements-dev.txt tests/ .pytest_cache/ __pycache__/ .git/

# Create startup script with better error handling
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "=== FastAPI Production Startup ==="\n\
echo "Environment: $NODE_ENV"\n\
echo "Debug: $DEBUG"\n\
echo "Workers: ${WORKERS:-4}"\n\
\n\
# Wait for database with timeout\n\
echo "Waiting for database connection..."\n\
timeout=60\n\
while ! pg_isready -h ${DATABASE_HOST:-pm_postgres_db} -p ${DATABASE_PORT:-5432} -U ${DATABASE_USER:-pm_user} -d ${DATABASE_NAME:-pm_database}; do\n\
  sleep 2\n\
  timeout=$((timeout-2))\n\
  if [ $timeout -le 0 ]; then\n\
    echo "Database connection timeout!"\n\
    exit 1\n\
  fi\n\
done\n\
\n\
echo "Database is ready. Initializing..."\n\
python init_db.py\n\
\n\
echo "Starting FastAPI application with Gunicorn..."\n\
exec gunicorn main:app \\\n\
  --bind 0.0.0.0:8000 \\\n\
  --workers ${WORKERS:-4} \\\n\
  --worker-class uvicorn.workers.UvicornWorker \\\n\
  --worker-connections 1000 \\\n\
  --max-requests 1000 \\\n\
  --max-requests-jitter 100 \\\n\
  --timeout 30 \\\n\
  --keep-alive 2 \\\n\
  --log-level ${LOG_LEVEL:-info} \\\n\
  --access-logfile - \\\n\
  --error-logfile - \\\n\
  --capture-output \\\n\
  --enable-stdio-inheritance\n\
' > /app/start.sh && chmod +x /app/start.sh

# Set ownership and switch to non-root user
RUN chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["/app/start.sh"]

# Alias for fastapi target (for compatibility)
FROM production AS fastapi 