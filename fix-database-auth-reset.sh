#!/bin/bash

# Fix PostgreSQL Authentication Issue
# This script resets the database with correct authentication settings

set -e

echo "🔧 Fixing PostgreSQL Authentication Issue..."
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "docker-compose is not installed or not in PATH"
    exit 1
fi

print_status "Step 1: Stopping all containers..."
docker-compose down

print_status "Step 2: Removing PostgreSQL volumes to reset database..."
docker volume rm $(docker volume ls -q | grep postgres) 2>/dev/null || print_warning "No postgres volumes found to remove"

print_status "Step 3: Removing any orphaned containers..."
docker-compose rm -f 2>/dev/null || true

print_status "Step 4: Starting PostgreSQL service first..."
docker-compose up -d pm_postgres_db

print_status "Step 5: Waiting for PostgreSQL to be ready..."
sleep 10

# Wait for PostgreSQL to be healthy
max_attempts=30
attempt=1
while [ $attempt -le $max_attempts ]; do
    if docker-compose exec -T pm_postgres_db pg_isready -U pm_user -d pm_database > /dev/null 2>&1; then
        print_status "PostgreSQL is ready!"
        break
    fi
    
    if [ $attempt -eq $max_attempts ]; then
        print_error "PostgreSQL failed to start after $max_attempts attempts"
        print_error "Checking logs..."
        docker-compose logs pm_postgres_db | tail -20
        exit 1
    fi
    
    echo "Waiting for PostgreSQL... (attempt $attempt/$max_attempts)"
    sleep 2
    ((attempt++))
done

print_status "Step 6: Verifying database connection..."
if docker-compose exec -T pm_postgres_db psql -U pm_user -d pm_database -c 'SELECT version();' > /dev/null 2>&1; then
    print_status "Database connection successful!"
else
    print_error "Database connection failed"
    print_error "Checking logs..."
    docker-compose logs pm_postgres_db | tail -20
    exit 1
fi

print_status "Step 7: Starting remaining services..."
docker-compose up -d

print_status "Step 8: Waiting for all services to be ready..."
sleep 15

print_status "Final verification..."
echo "================================================"
echo "Container Status:"
docker-compose ps

echo ""
echo "Database Connection Test:"
if docker-compose exec -T pm_postgres_db psql -U pm_user -d pm_database -c 'SELECT current_database(), current_user;' 2>/dev/null; then
    print_status "✅ Database authentication fixed successfully!"
    echo ""
    echo "You can now check the FastAPI logs:"
    echo "docker-compose logs fastapi"
else
    print_error "❌ Database connection still failing"
    echo ""
    echo "Check PostgreSQL logs:"
    echo "docker-compose logs pm_postgres_db"
fi

echo ""
echo "================================================"
echo "🎉 Fix completed!"
echo "================================================"