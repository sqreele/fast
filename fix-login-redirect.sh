#!/bin/bash

# Fix Login Redirect Issue in Production
# This script addresses the issue where login success redirects to localhost instead of production domain

set -e

echo "🔧 Fixing login redirect issue in production..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "docker-compose.prod.yml" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

# Check if .env.prod exists
if [ ! -f ".env.prod" ]; then
    print_error ".env.prod file not found. Please ensure production environment is configured."
    exit 1
fi

print_success "Environment files found"

# Verify NEXTAUTH_URL configuration
echo "📋 Checking NEXTAUTH_URL configuration..."
NEXTAUTH_URL=$(grep "NEXTAUTH_URL" .env.prod | cut -d'=' -f2)
echo "Current NEXTAUTH_URL: $NEXTAUTH_URL"

if [[ "$NEXTAUTH_URL" == *"localhost"* ]]; then
    print_warning "NEXTAUTH_URL contains localhost - this may cause redirect issues"
else
    print_success "NEXTAUTH_URL looks correct for production"
fi

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.prod.yml --env-file .env.prod down

# Rebuild frontend with fixes
echo "🔨 Rebuilding frontend with redirect fixes..."
docker-compose -f docker-compose.prod.yml --env-file .env.prod build frontend

# Start containers
echo "🚀 Starting containers with fixed configuration..."
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check container status
echo "📊 Checking container status..."
docker-compose -f docker-compose.prod.yml --env-file .env.prod ps

# Test the application
echo "🧪 Testing application..."
sleep 5

# Check if frontend is responding
FRONTEND_URL="http://206.189.89.239"
if curl -f -s "$FRONTEND_URL" > /dev/null; then
    print_success "Frontend is responding at $FRONTEND_URL"
else
    print_warning "Frontend may not be ready yet. Please wait a moment and try again."
fi

echo ""
print_success "Login redirect fix deployed!"
echo ""
echo "🔍 What was fixed:"
echo "   - Updated auth-utils.ts to use production IP instead of localhost"
echo "   - Enhanced NextAuth redirect callback with better logging"
echo "   - Added production URL validation in redirect logic"
echo ""
echo "🧪 To test the fix:"
echo "   1. Visit: $FRONTEND_URL/signin"
echo "   2. Login with valid credentials"
echo "   3. You should be redirected to $FRONTEND_URL instead of localhost"
echo ""
echo "📝 If issues persist, check the browser console for redirect logs"
echo "   and verify that NEXTAUTH_URL is set correctly in .env.prod"