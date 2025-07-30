#!/bin/bash

echo "=== Quick PostgreSQL Authentication Fix ==="
echo "This script will immediately fix the authentication issues"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is running
if ! sudo docker info >/dev/null 2>&1; then
    echo -e "${RED}Docker is not running. Starting Docker daemon...${NC}"
    sudo dockerd >/dev/null 2>&1 &
    sleep 5
fi

echo -e "${YELLOW}Step 1: Stopping containers and cleaning up...${NC}"
sudo docker-compose -f docker-compose.prod.yml down -v 2>/dev/null || true

echo -e "${YELLOW}Step 2: Removing old volumes and networks...${NC}"
sudo docker volume rm $(sudo docker volume ls -q | grep postgres) 2>/dev/null || true
sudo docker network rm $(sudo docker network ls -q --filter name=pm) 2>/dev/null || true

echo -e "${YELLOW}Step 3: Starting services with fresh database...${NC}"
sudo docker-compose -f docker-compose.prod.yml up --build -d

echo -e "${YELLOW}Step 4: Waiting for services to start...${NC}"
sleep 30

echo -e "${YELLOW}Step 5: Checking service status...${NC}"
sudo docker-compose -f docker-compose.prod.yml ps

echo -e "${GREEN}Fix completed! The authentication issues should now be resolved.${NC}"
echo ""
echo "To verify the fix:"
echo "1. Check logs: sudo docker-compose -f docker-compose.prod.yml logs pm_postgres_db"
echo "2. Test connection: sudo docker exec -it pm_postgres_db psql -U pm_user -d pm_database -c 'SELECT version();'"
echo ""
echo "If you still see authentication errors, the database may need more time to initialize."