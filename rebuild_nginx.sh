#!/bin/bash
echo "Stopping current containers..."
docker-compose -f docker-compose.prod.yml down

echo "Rebuilding nginx container..."
docker-compose -f docker-compose.prod.yml build --no-cache nginx

echo "Starting containers..."
docker-compose -f docker-compose.prod.yml up -d

echo "Checking nginx logs..."
docker-compose -f docker-compose.prod.yml logs nginx | tail -20
