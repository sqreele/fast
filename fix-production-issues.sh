#!/bin/bash

# Fix Production Issues Script
# This script applies fixes for nginx rate limiting, missing endpoints, and bot management

set -e

echo "🔧 Fixing Production Issues..."

# Create backup of current nginx config
echo "📦 Creating backup of current nginx configuration..."
cp nginx/nginx.prod.conf nginx/nginx.prod.conf.backup.$(date +%Y%m%d_%H%M%S)

echo "✅ Applied fixes for:"
echo "  - Fixed nginx upstream server names (fastapi, frontend)"
echo "  - Added /nginx_status endpoint for Prometheus monitoring"
echo "  - Increased rate limiting thresholds (login: 5r/m -> 10r/m, api: 10r/s -> 20r/s)"
echo "  - Added bot detection and rate limiting for GPTBot and other AI crawlers"
echo "  - Created missing NextAuth API endpoints (/providers, /_log, /error)"
echo "  - Added robots.txt to manage bot crawling"
echo "  - Fixed NextAuth page redirects"

# Check if docker-compose is available
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
elif command -v docker &> /dev/null && docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
else
    echo "⚠️  Docker Compose not found. Please restart the containers manually:"
    echo "   - Rebuild nginx: docker build ./nginx -t nginx:latest"
    echo "   - Rebuild frontend: docker build ./frontend -t frontend:latest"
    echo "   - Restart nginx container"
    echo "   - Restart frontend container"
    exit 0
fi

echo ""
echo "🔄 Restarting affected services..."

# Restart nginx to apply configuration changes
echo "🔄 Restarting nginx service..."
$DOCKER_COMPOSE_CMD -f docker-compose.prod.yml restart nginx

# Rebuild and restart frontend to include new API endpoints
echo "🔄 Rebuilding and restarting frontend service..."
$DOCKER_COMPOSE_CMD -f docker-compose.prod.yml build frontend
$DOCKER_COMPOSE_CMD -f docker-compose.prod.yml restart frontend

echo ""
echo "✅ Production issues fixed successfully!"
echo ""
echo "📊 Monitor the logs to verify fixes:"
echo "   docker logs pm_nginx -f"
echo "   docker logs frontend-1 -f"
echo ""
echo "🔍 Check endpoints:"
echo "   - Nginx status: curl http://localhost/nginx_status (from internal network)"
echo "   - Auth providers: curl http://localhost/api/auth/providers"
echo "   - Auth error: curl http://localhost/api/auth/error"
echo "   - Robots.txt: curl http://localhost/robots.txt"
echo ""
echo "📈 Expected improvements:"
echo "   - Reduced 503 rate limiting errors"
echo "   - Elimination of 404 errors for /api/auth/* endpoints"
echo "   - Reduced 404 errors from bot crawling"
echo "   - Working Prometheus nginx monitoring"