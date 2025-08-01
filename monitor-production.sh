#!/bin/bash

# Production Monitoring Script
# Quick health check and monitoring for production services

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

SERVER_IP="206.189.89.239"

echo -e "${BLUE}📊 Production Monitoring Dashboard${NC}"
echo "Server: $SERVER_IP"
echo "Time: $(date)"
echo ""

# Container Status
echo -e "${BLUE}🐳 Container Status:${NC}"
docker-compose -f docker-compose.prod.yml ps
echo ""

# Service Health Checks
echo -e "${BLUE}🔍 Health Checks:${NC}"

# Test nginx health endpoint
if curl -s -f "http://localhost/health" >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Nginx Health: OK${NC}"
else
    echo -e "${RED}❌ Nginx Health: FAILED${NC}"
fi

# Test API health
if curl -s -f "http://localhost/api/health" >/dev/null 2>&1; then
    echo -e "${GREEN}✅ API Health: OK${NC}"
else
    echo -e "${RED}❌ API Health: FAILED${NC}"
fi

# Test frontend
if curl -s -f "http://localhost/" >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend: OK${NC}"
else
    echo -e "${RED}❌ Frontend: FAILED${NC}"
fi

# External connectivity
echo ""
echo -e "${BLUE}🌐 External Connectivity:${NC}"
if curl -s -f "http://$SERVER_IP/health" >/dev/null 2>&1; then
    echo -e "${GREEN}✅ External Access: OK${NC}"
else
    echo -e "${RED}❌ External Access: FAILED${NC}"
fi

# Resource Usage
echo ""
echo -e "${BLUE}💻 Resource Usage:${NC}"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" | head -10

# Port Status
echo ""
echo -e "${BLUE}🔌 Port Status:${NC}"
echo "Active ports:"
ss -tulpn | grep -E ":80|:443|:3000|:8000" | awk '{print $1, $5}' | sort

# Recent Logs (errors)
echo ""
echo -e "${BLUE}📋 Recent Error Logs:${NC}"
docker-compose -f docker-compose.prod.yml logs --tail=5 --since=10m | grep -i error || echo "No recent errors found"

echo ""
echo -e "${BLUE}🔗 Quick Actions:${NC}"
echo "View logs:     docker-compose -f docker-compose.prod.yml logs -f"
echo "Restart all:   docker-compose -f docker-compose.prod.yml restart"
echo "Check nginx:   docker-compose -f docker-compose.prod.yml exec nginx nginx -t"
echo "Scale up:      docker-compose -f docker-compose.prod.yml up -d --scale fastapi=3 --scale frontend=3"
echo ""
echo "🌍 Application URLs:"
echo "   Frontend: http://$SERVER_IP/"
echo "   API Docs: http://$SERVER_IP/api/docs"
echo "   Health:   http://$SERVER_IP/health"