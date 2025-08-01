#!/bin/bash

# Quick Production Deployment Script
# Run this on your production server for a fast deployment

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🚀 Quick Production Deployment${NC}"
echo "Server: 206.189.89.239"
echo ""

# Step 1: Clean previous deployment
echo -e "${BLUE}📦 Cleaning previous deployment...${NC}"
docker-compose -f docker-compose.prod.yml down --remove-orphans

# Step 2: Deploy with environment file
echo -e "${BLUE}🏗️  Building and starting services...${NC}"
docker-compose -f docker-compose.prod.yml --env-file .env.prod up --build -d

# Step 3: Wait for services
echo -e "${BLUE}⏳ Waiting for services to start (30 seconds)...${NC}"
sleep 30

# Step 4: Show status
echo -e "${BLUE}📊 Service Status:${NC}"
docker-compose -f docker-compose.prod.yml ps

echo ""
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo "🌐 Test your application:"
echo "   • Frontend: http://206.189.89.239/"
echo "   • API Health: http://206.189.89.239/api/health"
echo "   • Nginx Health: http://206.189.89.239/health"
echo ""
echo "📋 Monitor with:"
echo "   docker-compose -f docker-compose.prod.yml logs -f"