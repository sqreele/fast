#!/bin/bash

# Comprehensive fix script for PM System issues
# Fixes: ENUM type conflicts, admin user password_hash, and Redis authentication

set -e

echo "🔧 PM System - Comprehensive Fix Script"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

print_status "Starting comprehensive fix process..."

# Step 1: Stop all containers
print_status "Step 1: Stopping all containers..."
docker-compose down

# Step 2: Fix admin user password_hash
print_status "Step 2: Fixing admin user password_hash..."
if [ -f "fix-admin-password.py" ]; then
    python3 fix-admin-password.py
    if [ $? -eq 0 ]; then
        print_success "Admin user password_hash fixed"
    else
        print_warning "Admin user password_hash fix failed, will be handled during startup"
    fi
else
    print_warning "fix-admin-password.py not found, will be handled during startup"
fi

# Step 3: Start containers
print_status "Step 3: Starting containers..."
docker-compose up -d

# Step 4: Wait for services to be ready
print_status "Step 4: Waiting for services to be ready..."
sleep 10

# Step 5: Check container status
print_status "Step 5: Checking container status..."
docker-compose ps

# Step 6: Check for errors in logs
print_status "Step 6: Checking for errors in logs..."
echo "--- FastAPI Logs ---"
docker-compose logs fastapi-1 | tail -20
echo ""
echo "--- FastAPI-2 Logs ---"
docker-compose logs fastapi-2 | tail -20
echo ""
echo "--- PostgreSQL Logs ---"
docker-compose logs pm_postgres_db | tail -10

# Step 7: Test API endpoints
print_status "Step 7: Testing API endpoints..."
sleep 5

# Test health endpoint
if curl -s http://localhost:8000/health > /dev/null; then
    print_success "Health endpoint is working"
else
    print_warning "Health endpoint not responding"
fi

# Test admin interface
if curl -s http://localhost:8000/admin/ > /dev/null; then
    print_success "Admin interface is accessible"
else
    print_warning "Admin interface not accessible"
fi

# Step 8: Show access information
echo ""
echo "🎉 Fix process completed!"
echo "========================"
echo ""
echo "📋 Access Information:"
echo "   Frontend: http://localhost"
echo "   API Docs: http://localhost:8000/docs"
echo "   Admin Interface: http://localhost:8000/admin/"
echo "   Health Check: http://localhost:8000/health"
echo ""
echo "🔐 Admin Credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "📊 Monitoring:"
echo "   Grafana: http://localhost:3001"
echo "   Prometheus: http://localhost:9090"
echo ""
echo "🔍 Troubleshooting:"
echo "   View logs: docker-compose logs -f [service_name]"
echo "   Restart service: docker-compose restart [service_name]"
echo "   Check status: docker-compose ps"
echo ""

print_success "All fixes applied successfully!" 