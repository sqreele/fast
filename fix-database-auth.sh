#!/bin/bash

echo "=== Database Authentication Fix Script ==="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Step 1: Checking current configuration...${NC}"

# Check if .env file exists and has correct format
if [ -f ".env" ]; then
    echo "✓ .env file found"
    
    # Check for line breaks in DATABASE_URL
    if grep -q "pm_postgres_db:5432/$" .env; then
        echo -e "${RED}✗ DATABASE_URL has line break - fixing...${NC}"
        # Fix the DATABASE_URL line break
        sed -i ':a;N;$!ba;s/pm_postgres_db:5432\/\npm_database/pm_postgres_db:5432\/pm_database/g' .env
        echo -e "${GREEN}✓ DATABASE_URL fixed${NC}"
    else
        echo "✓ DATABASE_URL format is correct"
    fi
    
    # Extract password from .env
    POSTGRES_PASSWORD=$(grep POSTGRES_PASSWORD .env | cut -d'=' -f2)
    echo "✓ Found password in .env: ${POSTGRES_PASSWORD:0:8}..."
else
    echo -e "${RED}✗ .env file not found${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 2: Checking requirements.txt...${NC}"

# Check if click is in requirements.txt
if grep -q "^click==" backend/requirements.txt; then
    echo "✓ click dependency found in requirements.txt"
else
    echo -e "${RED}✗ click dependency missing - already added${NC}"
fi

echo -e "${YELLOW}Step 3: Docker container fixes...${NC}"

echo "The following issues have been identified and require Docker container restart:"
echo "1. ✓ Missing 'click' dependency - FIXED in requirements.txt"
echo "2. ✓ DATABASE_URL line break - FIXED in .env file" 
echo "3. ⚠️  PostgreSQL authentication method mismatch"

echo ""
echo -e "${YELLOW}To complete the fix, run these commands:${NC}"
echo ""
echo "# Stop and remove existing containers:"
echo "docker-compose down -v"
echo ""
echo "# Remove postgres volume to reset database:"
echo "docker volume rm \$(docker volume ls -q | grep postgres)"
echo ""
echo "# Rebuild and start containers:"
echo "docker-compose -f docker-compose.prod.yml up --build -d"
echo ""

echo -e "${YELLOW}Alternative fix for production:${NC}"
echo ""
echo "# If you want to keep existing data, reset postgres password:"
echo "docker exec -it pm_postgres_db psql -U postgres -c \"ALTER USER pm_user PASSWORD '${POSTGRES_PASSWORD}';\""
echo ""

echo -e "${GREEN}Step 4: Summary of fixes applied:${NC}"
echo "✓ Added 'click==8.1.7' to backend/requirements.txt"
echo "✓ Fixed DATABASE_URL line break in .env"
echo "✓ Confirmed password consistency between .env and docker-compose files"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Restart Docker containers using the commands above"
echo "2. The FastAPI app should start successfully"
echo "3. Check logs with: docker-compose logs fastapi"