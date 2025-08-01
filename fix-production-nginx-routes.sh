#!/bin/bash

# Fix Production Nginx Routing Issues
# This script addresses the 404 errors seen in production logs

echo "🔧 Fixing Production Nginx Routing Issues..."

# Check if running as root or with sudo
if [[ $EUID -ne 0 ]] && ! sudo -n true 2>/dev/null; then
    echo "⚠️  This script requires sudo privileges to restart Docker services"
    echo "Please run with sudo or ensure user has Docker permissions"
fi

# Function to check if docker compose is available
check_docker() {
    if command -v docker >/dev/null 2>&1; then
        if docker compose version >/dev/null 2>&1; then
            DOCKER_CMD="docker compose"
        elif docker-compose --version >/dev/null 2>&1; then
            DOCKER_CMD="docker-compose"
        else
            echo "❌ Docker Compose not found. Please install Docker Compose"
            exit 1
        fi
    else
        echo "❌ Docker not found. Please install Docker"
        exit 1
    fi
    echo "✅ Using: $DOCKER_CMD"
}

# Function to backup current nginx config
backup_nginx_config() {
    echo "📦 Creating backup of current nginx configuration..."
    if [ -f "nginx/nginx.prod.conf" ]; then
        cp nginx/nginx.prod.conf nginx/nginx.prod.conf.backup.$(date +%Y%m%d_%H%M%S)
        echo "✅ Backup created"
    fi
}

# Function to validate nginx configuration
validate_nginx_config() {
    echo "🔍 Validating nginx configuration..."
    
    # Check if required files exist
    if [ ! -f "nginx/nginx.prod.conf" ]; then
        echo "❌ nginx.prod.conf not found"
        return 1
    fi
    
    # Check for required location blocks
    local required_locations=("/admin" "/api/" "/api/auth/" "/health")
    local missing_locations=()
    
    for location in "${required_locations[@]}"; do
        if ! grep -q "location $location" nginx/nginx.prod.conf; then
            missing_locations+=("$location")
        fi
    done
    
    if [ ${#missing_locations[@]} -eq 0 ]; then
        echo "✅ All required location blocks found"
        return 0
    else
        echo "❌ Missing location blocks: ${missing_locations[*]}"
        return 1
    fi
}

# Function to rebuild nginx container
rebuild_nginx() {
    echo "🏗️  Rebuilding nginx container with updated configuration..."
    
    # Stop nginx container
    $DOCKER_CMD -f docker-compose.prod.yml stop nginx 2>/dev/null || true
    
    # Remove nginx container
    $DOCKER_CMD -f docker-compose.prod.yml rm -f nginx 2>/dev/null || true
    
    # Rebuild nginx container
    $DOCKER_CMD -f docker-compose.prod.yml build nginx
    
    if [ $? -eq 0 ]; then
        echo "✅ Nginx container rebuilt successfully"
    else
        echo "❌ Failed to rebuild nginx container"
        return 1
    fi
}

# Function to restart services
restart_services() {
    echo "🔄 Restarting services..."
    
    # Start all services
    $DOCKER_CMD -f docker-compose.prod.yml up -d
    
    if [ $? -eq 0 ]; then
        echo "✅ Services started successfully"
    else
        echo "❌ Failed to start services"
        return 1
    fi
    
    # Wait for services to be healthy
    echo "⏳ Waiting for services to become healthy..."
    sleep 10
    
    # Check service status
    $DOCKER_CMD -f docker-compose.prod.yml ps
}

# Function to test routes
test_routes() {
    echo "🧪 Testing routes..."
    
    local base_url="http://localhost"
    local test_routes=(
        "/health"
        "/api/health" 
        "/api/v1/admin/"
        "/admin"
    )
    
    echo "Testing routes on $base_url"
    
    for route in "${test_routes[@]}"; do
        echo -n "Testing $route... "
        
        response=$(curl -s -o /dev/null -w "%{http_code}" "$base_url$route" 2>/dev/null)
        
        if [ "$response" = "200" ] || [ "$response" = "401" ] || [ "$response" = "403" ]; then
            echo "✅ $response"
        elif [ "$response" = "404" ]; then
            echo "❌ 404 (Route not found)"
        else
            echo "⚠️  $response"
        fi
    done
}

# Function to show recent logs
show_logs() {
    echo "📋 Recent nginx logs:"
    $DOCKER_CMD -f docker-compose.prod.yml logs --tail=20 nginx 2>/dev/null || echo "Could not fetch logs"
}

# Main execution
main() {
    echo "🚀 Starting nginx routing fix..."
    
    # Check prerequisites
    check_docker
    
    # Create backup
    backup_nginx_config
    
    # Validate configuration
    if validate_nginx_config; then
        echo "✅ Configuration validation passed"
    else
        echo "❌ Configuration validation failed"
        echo "Please check the nginx configuration manually"
        exit 1
    fi
    
    # Rebuild and restart
    if rebuild_nginx; then
        restart_services
        
        # Wait a moment for services to stabilize
        sleep 5
        
        # Test routes
        test_routes
        
        # Show recent logs
        show_logs
        
        echo ""
        echo "🎉 Nginx routing fix completed!"
        echo ""
        echo "✅ Fixed issues:"
        echo "   - Added missing /admin route"
        echo "   - Fixed NextAuth /api/auth/ routes"
        echo "   - Removed conflicting auth configuration"
        echo "   - Added /api/v1/admin/ root endpoint"
        echo ""
        echo "🔍 Monitor logs with:"
        echo "   $DOCKER_CMD -f docker-compose.prod.yml logs -f nginx"
        
    else
        echo "❌ Failed to rebuild nginx. Check the configuration and try again."
        exit 1
    fi
}

# Run main function
main "$@"