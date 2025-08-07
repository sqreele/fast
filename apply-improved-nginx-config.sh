#!/bin/bash

echo "=== Applying Improved Nginx Configuration ==="

# Backup current configuration
echo "1. Backing up current nginx configuration..."
cp nginx/nginx.prod.conf nginx/nginx.prod.conf.backup.$(date +%Y%m%d_%H%M%S)

# Replace with improved configuration
echo "2. Applying improved nginx configuration..."
cp nginx/nginx.prod.improved.conf nginx/nginx.prod.conf

# Update Docker Compose to rebuild nginx
echo "3. Rebuilding nginx container with new configuration..."
sudo docker-compose -f docker-compose.prod.yml build nginx

# Test the configuration
echo "4. Testing nginx configuration..."
sudo docker run --rm -v $(pwd)/nginx/nginx.prod.conf:/etc/nginx/nginx.conf nginx:latest nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx configuration is valid"
    
    echo "5. Restarting nginx with new configuration..."
    sudo docker-compose -f docker-compose.prod.yml stop nginx
    sudo docker-compose -f docker-compose.prod.yml up -d nginx
    
    echo "6. Checking nginx status..."
    sleep 5
    sudo docker logs pm_nginx --tail 10
    
    echo "=== Configuration Applied Successfully ==="
else
    echo "❌ Nginx configuration has errors. Restoring backup..."
    cp nginx/nginx.prod.conf.backup.* nginx/nginx.prod.conf
    echo "Backup restored. Please check the configuration."
    exit 1
fi