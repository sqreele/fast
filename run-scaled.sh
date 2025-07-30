#!/bin/bash

echo "Starting services with scaling..."
echo "Frontend: 2 instances"
echo "FastAPI: 2 instances"
echo ""
echo "All traffic will be routed through nginx on port 80"
echo "Frontend will be accessible at: http://localhost"
echo "API will be accessible at: http://localhost/api/v1"
echo ""

# Stop any existing containers
docker compose down

# Start with scaling
docker compose up -d --scale frontend=2 --scale fastapi=2

echo ""
echo "Services started!"
echo "Check status with: docker compose ps"
echo "View logs with: docker compose logs -f"
echo "Stop with: docker compose down"