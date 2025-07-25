#!/bin/bash
set -e

echo "=== Nginx Startup ==="
echo "Testing nginx configuration..."
nginx -t

echo "Starting nginx..."
exec nginx -g "daemon off;"
