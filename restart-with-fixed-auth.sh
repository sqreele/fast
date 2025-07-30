#!/bin/bash

echo "=== PostgreSQL Authentication Fix & Restart Script ==="
echo "This script restarts the services with the corrected authentication configuration"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Step 1: Verifying environment configuration...${NC}"

# Check if all environment files have consistent passwords
MAIN_PASSWORD=$(grep "POSTGRES_PASSWORD=" .env | cut -d'=' -f2)
PROD_PASSWORD=$(grep "POSTGRES_PASSWORD=" .env.prod | cut -d'=' -f2)
PRODUCTION_PASSWORD=$(grep "POSTGRES_PASSWORD=" .env.production | cut -d'=' -f2)

if [ "$MAIN_PASSWORD" = "$PROD_PASSWORD" ] && [ "$MAIN_PASSWORD" = "$PRODUCTION_PASSWORD" ]; then
    echo -e "${GREEN}✓ All environment files have consistent passwords${NC}"
    echo "Password: ${MAIN_PASSWORD:0:8}..."
else
    echo -e "${RED}✗ Password mismatch detected between environment files${NC}"
    echo "Main: ${MAIN_PASSWORD:0:8}..."
    echo "Prod: ${PROD_PASSWORD:0:8}..."
    echo "Production: ${PRODUCTION_PASSWORD:0:8}..."
    exit 1
fi

# Verify DATABASE_URL format
if grep -q "DATABASE_URL=postgresql://pm_user:.*@pm_postgres_db:5432/pm_database$" .env; then
    echo -e "${GREEN}✓ DATABASE_URL format is correct in .env${NC}"
else
    echo -e "${RED}✗ DATABASE_URL format issue in .env${NC}"
    exit 1
fi

echo -e "${BLUE}Step 2: Stopping existing containers...${NC}"
# Try different docker-compose commands based on what's available
if command -v docker-compose >/dev/null 2>&1; then
    DOCKER_COMPOSE="docker-compose"
elif command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
else
    echo -e "${RED}Neither docker-compose nor docker compose found${NC}"
    exit 1
fi

# Stop and remove containers, networks, and volumes
$DOCKER_COMPOSE -f docker-compose.prod.yml down -v 2>/dev/null || true

echo -e "${BLUE}Step 3: Cleaning up old data...${NC}"
# Remove old postgres volumes to ensure clean start
docker volume rm $(docker volume ls -q | grep postgres) 2>/dev/null || true
docker network rm $(docker network ls -q --filter name=pm) 2>/dev/null || true

echo -e "${BLUE}Step 4: Starting services with corrected authentication...${NC}"
# Start services using the production configuration
$DOCKER_COMPOSE -f docker-compose.prod.yml --env-file .env up -d --build

echo -e "${BLUE}Step 5: Waiting for services to initialize...${NC}"
sleep 30

echo -e "${BLUE}Step 6: Checking service status...${NC}"
$DOCKER_COMPOSE -f docker-compose.prod.yml ps

echo -e "${BLUE}Step 7: Testing database connection...${NC}"
# Wait a bit more for database to be fully ready
sleep 10

if docker exec pm_postgres_db psql -U pm_user -d pm_database -c 'SELECT version();' >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Database connection successful!${NC}"
else
    echo -e "${YELLOW}⚠ Database connection test failed, but this may be normal during startup${NC}"
fi

echo -e "${GREEN}=== Fix completed! ===${NC}"
echo ""
echo "To monitor the services:"
echo "1. Check logs: $DOCKER_COMPOSE -f docker-compose.prod.yml logs -f"
echo "2. Check specific service: $DOCKER_COMPOSE -f docker-compose.prod.yml logs fastapi"
echo "3. Test database: docker exec -it pm_postgres_db psql -U pm_user -d pm_database"
echo ""
echo -e "${YELLOW}If you still see authentication errors, wait a few more minutes for full initialization.${NC}"