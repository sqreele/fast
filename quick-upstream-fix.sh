#!/bin/bash

# Quick Fix for Upstream Issues
# This script provides a quick fix for common nginx upstream problems

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Quick Upstream Issues Fix           ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to print status
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is available
if ! command -v docker >/dev/null 2>&1; then
    print_error "Docker is not available"
    exit 1
fi

# Step 1: Check current status
print_status "Step 1: Checking current status..."
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" || echo "No containers running"
echo ""

# Step 2: Restart services
print_status "Step 2: Restarting services..."
if [ -f "docker-compose.prod.yml" ]; then
    print_status "Restarting all services..."
    docker compose -f docker-compose.prod.yml restart || print_warning "Some services may not have been running"
    
    print_status "Waiting for services to start..."
    sleep 30
    
    print_status "Current status after restart:"
    docker compose -f docker-compose.prod.yml ps
    echo ""
else
    print_error "docker-compose.prod.yml not found"
    exit 1
fi

# Step 3: Check if services are healthy
print_status "Step 3: Checking service health..."

# Check if nginx is running
if docker compose -f docker-compose.prod.yml ps nginx 2>/dev/null | grep -q "Up"; then
    print_success "Nginx is running"
    
    # Test nginx configuration
    if docker compose -f docker-compose.prod.yml exec -T nginx nginx -t >/dev/null 2>&1; then
        print_success "Nginx configuration is valid"
        
        # Reload nginx
        docker compose -f docker-compose.prod.yml exec -T nginx nginx -s reload
        print_success "Nginx reloaded"
    else
        print_error "Nginx configuration has errors"
    fi
else
    print_error "Nginx is not running"
fi

# Check if frontend is running
if docker compose -f docker-compose.prod.yml ps frontend 2>/dev/null | grep -q "Up"; then
    print_success "Frontend is running"
else
    print_error "Frontend is not running"
fi

# Check if fastapi is running
if docker compose -f docker-compose.prod.yml ps fastapi 2>/dev/null | grep -q "Up"; then
    print_success "FastAPI is running"
else
    print_error "FastAPI is not running"
fi

echo ""

# Step 4: Test connectivity
print_status "Step 4: Testing connectivity..."

# Test internal connectivity
if docker compose -f docker-compose.prod.yml ps nginx 2>/dev/null | grep -q "Up"; then
    print_status "Testing internal connectivity..."
    
    if docker compose -f docker-compose.prod.yml exec -T nginx curl -s -f http://fastapi:8000/health >/dev/null 2>&1; then
        print_success "Nginx can reach FastAPI backend"
    else
        print_error "Nginx cannot reach FastAPI backend"
    fi
    
    if docker compose -f docker-compose.prod.yml exec -T nginx curl -s -f http://frontend:3000/ >/dev/null 2>&1; then
        print_success "Nginx can reach Frontend"
    else
        print_error "Nginx cannot reach Frontend"
    fi
fi

# Test external connectivity
print_status "Testing external connectivity..."
for endpoint in "/health" "/api/health" "/"; do
    if curl -s -I "http://localhost$endpoint" 2>/dev/null | head -1 | grep -q "200\|301\|302"; then
        print_success "Local $endpoint - OK"
    else
        print_error "Local $endpoint - FAILED"
    fi
done
echo ""

# Step 5: Show recent logs
print_status "Step 5: Recent logs..."
echo "=== NGINX LOGS (last 5 lines) ==="
docker compose -f docker-compose.prod.yml logs --tail=5 nginx 2>/dev/null || echo "Nginx logs not available"
echo ""

echo "=== FRONTEND LOGS (last 5 lines) ==="
docker compose -f docker-compose.prod.yml logs --tail=5 frontend 2>/dev/null || echo "Frontend logs not available"
echo ""

echo "=== FASTAPI LOGS (last 5 lines) ==="
docker compose -f docker-compose.prod.yml logs --tail=5 fastapi 2>/dev/null || echo "FastAPI logs not available"
echo ""

# Step 6: Final status
print_status "Step 6: Final status..."
echo "=== CURRENT STATUS ==="
docker compose -f docker-compose.prod.yml ps
echo ""

print_success "Quick fix completed!"
echo ""
echo "If issues persist, try:"
echo "1. Run the diagnostic script: ./diagnose-upstream-issues.sh"
echo "2. Run the full fix script: ./fix-production-upstream-issues.sh"
echo "3. Check logs: docker compose -f docker-compose.prod.yml logs -f [service_name]"
echo ""