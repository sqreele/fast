#!/bin/bash

echo "=== Fixing Nginx Upstream Connection Issues ==="

# Stop the current deployment
echo "1. Stopping current containers..."
sudo docker-compose -f docker-compose.prod.yml down

# Clean up any dangling containers and networks
echo "2. Cleaning up Docker resources..."
sudo docker system prune -f
sudo docker network prune -f

# Remove any cached DNS resolution
echo "3. Flushing DNS cache..."
sudo systemctl restart systemd-resolved 2>/dev/null || echo "systemd-resolved not available"

# Check if images exist and are healthy
echo "4. Checking Docker images..."
sudo docker images | grep -E "(pm-frontend|pm-fastapi)"

# Rebuild frontend image to ensure it's working
echo "5. Rebuilding frontend image..."
sudo docker-compose -f docker-compose.prod.yml build frontend

# Start database and redis first
echo "6. Starting database and redis..."
sudo docker-compose -f docker-compose.prod.yml up -d pm_postgres_db redis

# Wait for database to be ready
echo "7. Waiting for database to be ready..."
sleep 30

# Start backend services
echo "8. Starting backend services..."
sudo docker-compose -f docker-compose.prod.yml up -d fastapi

# Wait for backend to be ready
echo "9. Waiting for backend to be ready..."
sleep 20

# Start frontend services
echo "10. Starting frontend services..."
sudo docker-compose -f docker-compose.prod.yml up -d frontend

# Wait for frontend to be ready
echo "11. Waiting for frontend to be ready..."
sleep 30

# Start nginx last
echo "12. Starting nginx..."
sudo docker-compose -f docker-compose.prod.yml up -d nginx

# Check status
echo "13. Checking container status..."
sudo docker-compose -f docker-compose.prod.yml ps

# Test nginx upstream health
echo "14. Testing nginx configuration..."
sudo docker exec pm_nginx nginx -t

# Check nginx upstream status
echo "15. Checking upstream servers..."
sudo docker exec pm_nginx cat /etc/hosts
sudo docker exec pm_nginx nslookup frontend 2>/dev/null || echo "DNS resolution test"

# Test frontend connectivity from nginx container
echo "16. Testing frontend connectivity from nginx..."
sudo docker exec pm_nginx curl -s -o /dev/null -w "%{http_code}" http://frontend:3000 || echo "Frontend connection test failed"

# Show recent nginx logs
echo "17. Recent nginx logs:"
sudo docker logs pm_nginx --tail 20

echo "=== Fix Complete ==="
echo "Monitor the logs with: sudo docker logs -f pm_nginx"