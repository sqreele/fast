#!/bin/bash

# Fix PostgreSQL Password Authentication (Data Preserving)
# This script fixes the password without resetting the database

set -e

echo "🔧 Fixing PostgreSQL Password Authentication..."
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

# Expected password from docker-compose.yml
EXPECTED_PASSWORD="QlILLYN4kmmkuDzNwGrEsBQ4M"

print_status "Step 1: Checking if PostgreSQL container is running..."
if ! docker-compose ps pm_postgres_db | grep -q "Up"; then
    print_warning "PostgreSQL container is not running. Starting it..."
    docker-compose up -d pm_postgres_db
    sleep 10
fi

print_status "Step 2: Connecting as postgres superuser to reset pm_user password..."
if docker-compose exec -T pm_postgres_db psql -U postgres -c "ALTER USER pm_user PASSWORD '$EXPECTED_PASSWORD';" 2>/dev/null; then
    print_status "Password updated successfully!"
else
    print_error "Failed to update password as postgres user"
    print_warning "Trying alternative approach..."
    
    # Try to connect as postgres and create/recreate the user
    if docker-compose exec -T pm_postgres_db psql -U postgres -c "DROP USER IF EXISTS pm_user; CREATE USER pm_user WITH PASSWORD '$EXPECTED_PASSWORD'; GRANT ALL PRIVILEGES ON DATABASE pm_database TO pm_user; ALTER DATABASE pm_database OWNER TO pm_user;" 2>/dev/null; then
        print_status "User recreated successfully!"
    else
        print_error "Failed to recreate user. Database may need to be reset."
        exit 1
    fi
fi

print_status "Step 3: Testing database connection with new password..."
sleep 2

if docker-compose exec -T pm_postgres_db psql -U pm_user -d pm_database -c 'SELECT current_database(), current_user;' 2>/dev/null; then
    print_status "✅ Database connection successful!"
else
    print_error "❌ Database connection still failing"
    print_error "You may need to run the full reset script: ./fix-database-auth-reset.sh"
    exit 1
fi

print_status "Step 4: Restarting FastAPI service to reconnect with correct password..."
docker-compose restart fastapi

print_status "Step 5: Waiting for FastAPI to start..."
sleep 10

print_status "Final verification..."
echo "================================================"
echo "Container Status:"
docker-compose ps

echo ""
echo "FastAPI Logs (last 10 lines):"
docker-compose logs --tail=10 fastapi

echo ""
echo "================================================"
echo "🎉 Password fix completed!"
echo ""
echo "If you still see authentication errors, run:"
echo "  ./fix-database-auth-reset.sh"
echo "================================================"