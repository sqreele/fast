#!/bin/bash

echo "Stopping existing containers..."
docker-compose down 2>/dev/null || docker compose down 2>/dev/null || true

echo "Removing any existing images to force rebuild..."
docker-compose down --rmi all 2>/dev/null || docker compose down --rmi all 2>/dev/null || true

echo "Building and starting development environment..."
if command -v docker-compose &> /dev/null; then
    docker-compose -f docker-compose.yml -f docker-compose.override.yml up --build
elif command -v docker &> /dev/null; then
    docker compose -f docker-compose.yml -f docker-compose.override.yml up --build
else
    echo "Docker is not available. Please ensure Docker is installed and running."
    exit 1
fi