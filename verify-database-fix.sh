#!/bin/bash

echo "=== PostgreSQL Authentication Fix Verification ==="
echo "This script verifies that the DATABASE_URL issue has been resolved"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Step 1: Checking DATABASE_URL format...${NC}"

# Check if DATABASE_URL is properly formatted (single line)
if grep -q "DATABASE_URL=postgresql://pm_user:.*@pm_postgres_db:5432/pm_database$" .env; then
    echo -e "${GREEN}✓ DATABASE_URL is correctly formatted on a single line${NC}"
    echo "DATABASE_URL: $(grep 'DATABASE_URL=' .env)"
else
    echo -e "${RED}✗ DATABASE_URL format issue still exists${NC}"
    echo "Current DATABASE_URL:"
    grep -A1 "DATABASE_URL" .env
    exit 1
fi

echo -e "${BLUE}Step 2: Checking password consistency...${NC}"

# Extract passwords
POSTGRES_PASSWORD=$(grep "POSTGRES_PASSWORD=" .env | cut -d'=' -f2)
DB_URL_PASSWORD=$(grep "DATABASE_URL=" .env | sed 's/.*:\/\/pm_user:\([^@]*\)@.*/\1/')

if [ "$POSTGRES_PASSWORD" = "$DB_URL_PASSWORD" ]; then
    echo -e "${GREEN}✓ Passwords match between POSTGRES_PASSWORD and DATABASE_URL${NC}"
    echo "Password: ${POSTGRES_PASSWORD:0:8}..."
else
    echo -e "${RED}✗ Password mismatch detected${NC}"
    echo "POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:0:8}..."
    echo "DATABASE_URL password: ${DB_URL_PASSWORD:0:8}..."
    exit 1
fi

echo -e "${GREEN}=== All fixes verified successfully! ===${NC}"
echo ""
echo -e "${YELLOW}The root cause of the authentication failure has been fixed:${NC}"
echo "- DATABASE_URL was broken across multiple lines in .env file"
echo "- This caused malformed connection strings leading to authentication failures"
echo "- The URL is now properly formatted on a single line"
echo ""
echo -e "${BLUE}To restart your services and apply the fix:${NC}"
echo ""
echo "1. If using Docker Compose directly:"
echo "   docker-compose down -v"
echo "   docker-compose up -d --build"
echo ""
echo "2. If using production setup:"
echo "   docker-compose -f docker-compose.prod.yml down -v"
echo "   docker-compose -f docker-compose.prod.yml up -d --build"
echo ""
echo "3. Using the provided restart script:"
echo "   sudo ./restart-with-fixed-auth.sh"
echo ""
echo -e "${YELLOW}The authentication errors should be resolved after restart.${NC}"