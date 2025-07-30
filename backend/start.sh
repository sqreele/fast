#!/bin/bash
set -e

echo "=== FastAPI Startup ==="
echo "Environment: $NODE_ENV"
echo "Database URL: ${DATABASE_URL}"

echo "Starting FastAPI server with simple configuration for testing..."

exec uvicorn main_simple:app --host 0.0.0.0 --port 8000 --log-level info 