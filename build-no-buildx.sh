#!/bin/bash

# Build script that avoids Docker buildx and bake issues
set -e

echo "=== PM System Build (No BuildX) ==="

# Function to build with retry logic
build_with_retry() {
    local service=$1
    local dockerfile=$2
    local context=$3
    local max_attempts=3
    
    for attempt in $(seq 1 $max_attempts); do
        echo "Building $service (attempt $attempt/$max_attempts)..."
        
        if [ -n "$dockerfile" ]; then
            if docker build -f "$dockerfile" -t "pm-$service:latest" "$context"; then
                echo "✅ Successfully built $service"
                return 0
            fi
        else
            if docker build -t "pm-$service:latest" "$context"; then
                echo "✅ Successfully built $service"
                return 0
            fi
        fi
        
        if [ $attempt -lt $max_attempts ]; then
            echo "⚠️  Build failed, retrying in 5 seconds..."
            sleep 5
            # Clean up any partial builds
            docker builder prune -f || true
        else
            echo "❌ Failed to build $service after $max_attempts attempts"
            return 1
        fi
    done
}

# Build backend with simple Dockerfile first, fallback to original
echo "Building FastAPI backend..."
if [ -f "backend/Dockerfile.simple" ]; then
    echo "Using simplified Dockerfile..."
    build_with_retry "fastapi" "backend/Dockerfile.simple" "backend/"
elif build_with_retry "fastapi" "backend/Dockerfile" "backend/"; then
    echo "Built with original Dockerfile"
else
    echo "❌ Failed to build backend"
    exit 1
fi

# Build frontend
echo "Building Next.js frontend..."
if build_with_retry "frontend" "" "frontend/"; then
    echo "✅ Frontend built successfully"
else
    echo "❌ Failed to build frontend"
    exit 1
fi

# Build nginx
echo "Building Nginx..."
if build_with_retry "nginx" "" "nginx/"; then
    echo "✅ Nginx built successfully"
else
    echo "❌ Failed to build nginx"
    exit 1
fi

echo ""
echo "=== Build Complete ==="
echo "All services built successfully!"
echo ""
echo "To start the services:"
echo "  Development: docker-compose up -d"
echo "  Production:  docker-compose -f docker-compose.prod.yml up -d"
echo ""
echo "To view images: docker images | grep pm-"