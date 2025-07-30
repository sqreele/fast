#!/bin/bash

echo "=== PostgreSQL Authentication Fix Script ==="
echo "This script fixes the authentication issues seen in the logs"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Step 1: Checking environment configuration...${NC}"

# Verify .env file has correct DATABASE_URL format
if grep -q "DATABASE_URL=postgresql://pm_user:.*@pm_postgres_db:5432/pm_database$" .env; then
    echo -e "${GREEN}✓ DATABASE_URL format is correct${NC}"
else
    echo -e "${RED}✗ DATABASE_URL format issue detected${NC}"
    echo "Current DATABASE_URL:"
    grep "DATABASE_URL" .env || echo "DATABASE_URL not found"
    exit 1
fi

# Extract and verify password consistency
POSTGRES_PASSWORD=$(grep "POSTGRES_PASSWORD=" .env | cut -d'=' -f2)
DB_URL_PASSWORD=$(grep "DATABASE_URL=" .env | sed 's/.*:\/\/pm_user:\([^@]*\)@.*/\1/')

echo -e "${BLUE}Step 2: Verifying password consistency...${NC}"
if [ "$POSTGRES_PASSWORD" = "$DB_URL_PASSWORD" ]; then
    echo -e "${GREEN}✓ Passwords match between POSTGRES_PASSWORD and DATABASE_URL${NC}"
    echo "Password: ${POSTGRES_PASSWORD:0:8}..."
else
    echo -e "${RED}✗ Password mismatch detected${NC}"
    echo "POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:0:8}..."
    echo "DATABASE_URL password: ${DB_URL_PASSWORD:0:8}..."
    exit 1
fi

echo -e "${BLUE}Step 3: Checking Docker Compose configuration...${NC}"

# Check if production compose file uses environment variables correctly
if grep -q "POSTGRES_PASSWORD: \${POSTGRES_PASSWORD" docker-compose.prod.yml; then
    echo -e "${GREEN}✓ Production compose file uses environment variable${NC}"
else
    echo -e "${YELLOW}⚠ Production compose file may have hardcoded password${NC}"
fi

echo -e "${BLUE}Step 4: Database authentication fix commands...${NC}"
echo ""
echo -e "${YELLOW}The following commands will fix the authentication issues:${NC}"
echo ""

echo "# 1. Stop all containers and remove volumes (DESTRUCTIVE - will lose data)"
echo "sudo docker-compose -f docker-compose.prod.yml down -v"
echo ""

echo "# 2. Remove any existing postgres volumes"
echo "sudo docker volume rm \$(sudo docker volume ls -q | grep postgres) 2>/dev/null || true"
echo ""

echo "# 3. Remove any existing networks"
echo "sudo docker network rm \$(sudo docker network ls -q --filter name=pm) 2>/dev/null || true"
echo ""

echo "# 4. Start with fresh database (recommended)"
echo "sudo docker-compose -f docker-compose.prod.yml up --build -d"
echo ""

echo -e "${YELLOW}Alternative: Reset password in existing database (preserves data)${NC}"
echo ""
echo "# If containers are running, reset the password:"
echo "sudo docker exec -it pm_postgres_db psql -U postgres -c \"ALTER USER pm_user PASSWORD '$POSTGRES_PASSWORD';\""
echo ""

echo -e "${BLUE}Step 5: Verification commands...${NC}"
echo ""
echo "# Check container status:"
echo "sudo docker-compose -f docker-compose.prod.yml ps"
echo ""
echo "# Check logs for authentication errors:"
echo "sudo docker-compose -f docker-compose.prod.yml logs pm_postgres_db | tail -20"
echo ""
echo "# Test database connection:"
echo "sudo docker exec -it pm_postgres_db psql -U pm_user -d pm_database -c 'SELECT version();'"
echo ""

echo -e "${GREEN}Summary of identified issues from logs:${NC}"
echo "1. ✓ Multiple services (172.18.0.6, 172.18.0.8) failing password authentication"
echo "2. ✓ PostgreSQL is running and accepting local connections"  
echo "3. ✓ Authentication method is scram-sha-256 (line 100 in pg_hba.conf)"
echo "4. ✓ DATABASE_URL line break fixed in .env file"
echo "5. ✓ Password consistency verified"
echo ""

echo -e "${YELLOW}Root cause analysis:${NC}"
echo "- Services are using correct username (pm_user) and database (pm_database)"
echo "- Password authentication is failing, likely due to:"
echo "  a) Password hash mismatch in PostgreSQL vs environment"
echo "  b) Authentication method incompatibility"
echo "  c) Corrupted user credentials in database"
echo ""

echo -e "${YELLOW}Recommended action:${NC}"
echo "Run the database reset commands above to ensure clean authentication setup."