#!/bin/bash

# Quick Diagnostic Script for Upstream Issues
# This script helps identify the root cause of nginx upstream problems

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Upstream Issues Diagnostic Tool     ${NC}"
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

# Step 1: Check container status
print_status "Step 1: Container Status Analysis"
echo "======================================"

echo "Running containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" || echo "No containers running"
echo ""

echo "All containers (including stopped):"
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" || echo "No containers found"
echo ""

# Step 2: Check Docker Compose status
print_status "Step 2: Docker Compose Status"
echo "=================================="

if [ -f "docker-compose.prod.yml" ]; then
    echo "Docker Compose services status:"
    docker compose -f docker-compose.prod.yml ps 2>/dev/null || echo "Docker Compose not running"
    echo ""
else
    print_error "docker-compose.prod.yml not found"
fi

# Step 3: Check network connectivity
print_status "Step 3: Network Analysis"
echo "=============================="

echo "Docker networks:"
docker network ls
echo ""

echo "Network details for pm_network:"
docker network inspect pm_network 2>/dev/null || print_warning "pm_network not found"
echo ""

# Step 4: Check port usage
print_status "Step 4: Port Usage Analysis"
echo "================================="

echo "Ports in use:"
for port in 80 443 3000 8000 5432 6379; do
    if ss -tulpn 2>/dev/null | grep ":$port " >/dev/null; then
        print_success "Port $port is in use"
        ss -tulpn 2>/dev/null | grep ":$port " || echo "   Details not available"
    else
        print_warning "Port $port is not in use"
    fi
done
echo ""

# Step 5: Check service logs
print_status "Step 5: Service Logs Analysis"
echo "==================================="

if [ -f "docker-compose.prod.yml" ]; then
    echo "Recent nginx logs (last 10 lines):"
    docker compose -f docker-compose.prod.yml logs --tail=10 nginx 2>/dev/null || echo "Nginx logs not available"
    echo ""
    
    echo "Recent frontend logs (last 10 lines):"
    docker compose -f docker-compose.prod.yml logs --tail=10 frontend 2>/dev/null || echo "Frontend logs not available"
    echo ""
    
    echo "Recent fastapi logs (last 10 lines):"
    docker compose -f docker-compose.prod.yml logs --tail=10 fastapi 2>/dev/null || echo "FastAPI logs not available"
    echo ""
fi

# Step 6: Check environment configuration
print_status "Step 6: Environment Configuration"
echo "======================================"

if [ -f ".env.prod" ]; then
    print_success ".env.prod file exists"
    echo "Environment variables (sensitive data masked):"
    cat .env.prod | sed 's/\(PASSWORD\|SECRET\|KEY\)=.*/\1=***MASKED***/' || echo "Could not read .env.prod"
else
    print_error ".env.prod file not found"
fi
echo ""

# Step 7: Check nginx configuration
print_status "Step 7: Nginx Configuration"
echo "================================"

if [ -f "nginx/nginx.prod.conf" ]; then
    print_success "nginx.prod.conf exists"
    
    # Check if nginx container is running and test config
    if docker compose -f docker-compose.prod.yml ps nginx 2>/dev/null | grep -q "Up"; then
        echo "Testing nginx configuration:"
        docker compose -f docker-compose.prod.yml exec -T nginx nginx -t 2>/dev/null && print_success "Nginx config is valid" || print_error "Nginx config has errors"
    else
        print_warning "Nginx container is not running"
    fi
else
    print_error "nginx.prod.conf not found"
fi
echo ""

# Step 8: Test connectivity
print_status "Step 8: Connectivity Tests"
echo "================================"

# Test local endpoints
echo "Testing local endpoints:"
for endpoint in "/health" "/api/health" "/"; do
    if curl -s -I "http://localhost$endpoint" 2>/dev/null | head -1 | grep -q "200\|301\|302"; then
        print_success "Local $endpoint - OK"
    else
        print_error "Local $endpoint - FAILED"
    fi
done
echo ""

# Test internal connectivity if containers are running
if docker compose -f docker-compose.prod.yml ps nginx 2>/dev/null | grep -q "Up"; then
    echo "Testing internal connectivity from nginx container:"
    
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
else
    print_warning "Nginx container not running - skipping internal connectivity tests"
fi
echo ""

# Step 9: Resource usage
print_status "Step 9: Resource Usage"
echo "==========================="

echo "Docker system info:"
docker system df 2>/dev/null || echo "Docker system info not available"
echo ""

echo "Disk usage:"
df -h . 2>/dev/null || echo "Disk usage info not available"
echo ""

echo "Memory usage:"
free -h 2>/dev/null || echo "Memory info not available"
echo ""

# Step 10: Recommendations
print_status "Step 10: Issue Analysis and Recommendations"
echo "=================================================="

echo "Based on the analysis above, here are the likely issues and solutions:"
echo ""

# Check if containers are running
running_containers=$(docker ps --format "{{.Names}}" 2>/dev/null | wc -l)
if [ "$running_containers" -eq 0 ]; then
    print_error "No containers are running"
    echo "   Solution: Start the services with: docker compose -f docker-compose.prod.yml --env-file .env.prod up -d"
    echo ""
fi

# Check if nginx is running
if ! docker ps --format "{{.Names}}" 2>/dev/null | grep -q "nginx"; then
    print_error "Nginx container is not running"
    echo "   Solution: Start nginx with: docker compose -f docker-compose.prod.yml up -d nginx"
    echo ""
fi

# Check if frontend is running
if ! docker ps --format "{{.Names}}" 2>/dev/null | grep -q "frontend"; then
    print_error "Frontend container is not running"
    echo "   Solution: Start frontend with: docker compose -f docker-compose.prod.yml up -d frontend"
    echo ""
fi

# Check if fastapi is running
if ! docker ps --format "{{.Names}}" 2>/dev/null | grep -q "fastapi"; then
    print_error "FastAPI container is not running"
    echo "   Solution: Start fastapi with: docker compose -f docker-compose.prod.yml up -d fastapi"
    echo ""
fi

# Check if database is running
if ! docker ps --format "{{.Names}}" 2>/dev/null | grep -q "postgres"; then
    print_error "PostgreSQL container is not running"
    echo "   Solution: Start database with: docker compose -f docker-compose.prod.yml up -d pm_postgres_db"
    echo ""
fi

echo "Common upstream issues and solutions:"
echo "1. Connection refused (111): Container is not running or not listening on the expected port"
echo "2. No live upstreams: All servers in the upstream group are down or unreachable"
echo "3. Connection timeout: Container is starting slowly or has resource constraints"
echo ""
echo "Quick fixes to try:"
echo "1. Restart all services: docker compose -f docker-compose.prod.yml restart"
echo "2. Rebuild and restart: docker compose -f docker-compose.prod.yml up -d --build"
echo "3. Check logs: docker compose -f docker-compose.prod.yml logs -f [service_name]"
echo "4. Run the full fix script: ./fix-production-upstream-issues.sh"
echo ""

print_success "Diagnostic complete!"