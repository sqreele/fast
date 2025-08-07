#!/bin/bash

# Test script to verify routing fixes
# This script tests the endpoints that were having 404 issues

echo "🔍 Testing routing fixes..."
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Base URL - adjust based on your environment
BASE_URL="http://localhost"

# Function to test endpoint
test_endpoint() {
    local url=$1
    local expected_status=$2
    local description=$3
    
    echo -n "Testing $description... "
    
    response=$(curl -s -w "%{http_code}" -o /dev/null "$url" 2>/dev/null)
    
    if [ "$response" = "$expected_status" ]; then
        echo -e "${GREEN}✓ PASS${NC} (HTTP $response)"
    else
        echo -e "${RED}✗ FAIL${NC} (HTTP $response, expected $expected_status)"
    fi
}

echo "1. Testing FastAPI metrics endpoint..."
test_endpoint "$BASE_URL/metrics" "200" "FastAPI /metrics"

echo ""
echo "2. Testing nginx status endpoint..."
test_endpoint "$BASE_URL/nginx_status" "403" "Nginx status (should be restricted)"

echo ""
echo "3. Testing auth endpoints (without auth - should get 401/422)..."
test_endpoint "$BASE_URL/api/v1/auth/me" "401" "Auth /me endpoint"

echo ""
echo "4. Testing health endpoint..."
test_endpoint "$BASE_URL/health" "200" "Health check"

echo ""
echo "5. Testing API base path..."
test_endpoint "$BASE_URL/api/v1/auth/verify-token" "401" "Token verification"

echo ""
echo "================================"
echo "🏁 Test completed!"
echo ""
echo "📝 Notes:"
echo "- /metrics should return 200 (now available)"
echo "- /nginx_status should return 403 (access restricted)"
echo "- Auth endpoints should return 401 (unauthorized) not 404"
echo "- Health endpoint should return 200"
echo ""
echo "If you're still getting 404s, make sure to:"
echo "1. Rebuild the FastAPI container: docker-compose build fastapi"
echo "2. Rebuild the nginx container: docker-compose build nginx"  
echo "3. Restart the services: docker-compose restart"