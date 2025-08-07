#!/bin/bash

# Test 404 Fixes Script
# This script tests the fixes for the 404 errors

set -e

echo "🧪 Testing 404 error fixes..."

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

# Test metrics endpoint
print_status "Testing /metrics endpoint..."
if curl -f http://localhost:8000/metrics > /dev/null 2>&1; then
    print_success "✅ /metrics endpoint is working"
    # Show a sample of the metrics
    echo "Sample metrics output:"
    curl -s http://localhost:8000/metrics | head -10
else
    print_error "❌ /metrics endpoint is not working"
fi

echo ""

# Test auth endpoint directly on FastAPI
print_status "Testing /api/v1/auth/me endpoint on FastAPI..."
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/auth/me)
if [ "$response" = "401" ]; then
    print_success "✅ /api/v1/auth/me endpoint is accessible (401 is expected without auth)"
elif [ "$response" = "404" ]; then
    print_error "❌ /api/v1/auth/me endpoint returns 404"
else
    print_warning "⚠️  /api/v1/auth/me endpoint returned $response"
fi

echo ""

# Test through nginx proxy
print_status "Testing /api/v1/auth/me through nginx..."
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/api/v1/auth/me)
if [ "$response" = "401" ]; then
    print_success "✅ Nginx routing to /api/v1/auth/me is working (401 is expected without auth)"
elif [ "$response" = "404" ]; then
    print_error "❌ Nginx routing to /api/v1/auth/me returns 404"
else
    print_warning "⚠️  Nginx routing to /api/v1/auth/me returned $response"
fi

echo ""

# Test the problematic double /api prefix
print_status "Testing double /api prefix (should not work)..."
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/api/api/v1/auth/me)
if [ "$response" = "404" ]; then
    print_success "✅ Double /api prefix correctly returns 404 (as expected)"
else
    print_warning "⚠️  Double /api prefix returned $response (should be 404)"
fi

echo ""

# Test health endpoint
print_status "Testing /health endpoint..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_success "✅ /health endpoint is working"
    echo "Health check response:"
    curl -s http://localhost:8000/health
else
    print_error "❌ /health endpoint is not working"
fi

echo ""

# Check service status
print_status "Checking service status..."
docker-compose -f docker-compose.prod.yml ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

echo ""

print_success "🎉 Testing completed!"
print_status "Summary:"
echo "  - Metrics endpoint should be working"
echo "  - Auth endpoints should be accessible (401 without auth is normal)"
echo "  - Double /api prefix should return 404"
echo "  - Health endpoint should be working"