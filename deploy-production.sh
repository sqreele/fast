#!/bin/bash

# Production deployment script for PM System
set -e

echo "=== PM System Production Deployment ==="

# Check if .env.prod exists
if [ ! -f ".env.prod" ]; then
    echo "Error: .env.prod file not found!"
    echo "Please create .env.prod with your production environment variables."
    exit 1
fi

# Load environment variables
export $(cat .env.prod | grep -v '^#' | xargs)

echo "Environment variables loaded from .env.prod"

# Stop any existing containers
echo "Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down --remove-orphans

# Remove old images (optional - uncomment if you want to force rebuild)
# echo "Removing old images..."
# docker-compose -f docker-compose.prod.yml down --rmi all

# Build and start services
echo "Building and starting production services..."
docker-compose -f docker-compose.prod.yml up --build -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 30

# Check service health
echo "Checking service health..."
docker-compose -f docker-compose.prod.yml ps

echo "=== Deployment Complete ==="
echo "Services should be available at:"
echo "- Frontend: http://localhost"
echo "- Backend API: http://localhost/api/v1"
echo "- Admin Interface: http://localhost:8081"
echo "- Monitoring: http://localhost:3001 (if monitoring enabled)"

echo ""
echo "To view logs, run: docker-compose -f docker-compose.prod.yml logs -f"
echo "To stop services, run: docker-compose -f docker-compose.prod.yml down"