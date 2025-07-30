#!/bin/bash

# Development deployment script for PM System
set -e

echo "=== PM System Development Deployment ==="

# Stop any existing containers
echo "Stopping existing containers..."
docker-compose down --remove-orphans

# Build and start services
echo "Building and starting development services..."
docker-compose up --build -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 20

# Check service health
echo "Checking service health..."
docker-compose ps

echo "=== Development Deployment Complete ==="
echo "Services should be available at:"
echo "- Frontend: http://localhost:3000"
echo "- Backend API: http://localhost:8000"
echo "- Database Admin: http://localhost:8081"
echo "- PostgreSQL: localhost:15432"

echo ""
echo "To view logs, run: docker-compose logs -f [service_name]"
echo "To stop services, run: docker-compose down"
echo "To rebuild specific service: docker-compose up --build [service_name]"