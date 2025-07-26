#!/bin/bash

# NextAuth CLIENT_FETCH_ERROR Fix Script
# This script diagnoses and fixes common NextAuth connectivity issues

echo "🔍 Diagnosing NextAuth CLIENT_FETCH_ERROR..."

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is available
if command -v docker &> /dev/null; then
    DOCKER_AVAILABLE=true
    print_status "Docker detected"
else
    DOCKER_AVAILABLE=false
    print_warning "Docker not available, checking local services"
fi

# Function to check service health
check_service_health() {
    local service_name="$1"
    local url="$2"
    local expected_status="${3:-200}"
    
    print_status "Checking $service_name at $url"
    
    if curl -s -o /dev/null -w "%{http_code}" "$url" | grep -q "$expected_status"; then
        print_success "$service_name is healthy"
        return 0
    else
        print_error "$service_name is not responding correctly"
        return 1
    fi
}

# Function to check backend health specifically
check_backend_health() {
    local backend_url="$1"
    print_status "Testing backend connectivity..."
    
    # Try multiple common health endpoints
    for endpoint in "/health" "/api/health" "/api/v1/health" "/docs"; do
        local full_url="${backend_url}${endpoint}"
        print_status "Trying $full_url"
        
        local response=$(curl -s -w "%{http_code}" "$full_url" 2>/dev/null)
        local status_code="${response: -3}"
        
        if [[ "$status_code" =~ ^[23] ]]; then
            print_success "Backend responding at $full_url (HTTP $status_code)"
            return 0
        fi
    done
    
    print_error "Backend is not responding on any health endpoint"
    return 1
}

# Function to restart Docker services
restart_docker_services() {
    print_status "Restarting Docker services in correct order..."
    
    # Stop services in reverse dependency order
    docker-compose stop nginx frontend fastapi 2>/dev/null || true
    
    # Wait a moment
    sleep 3
    
    # Start services in dependency order
    docker-compose up -d pm_postgres_db redis
    print_status "Waiting for database and Redis to be ready..."
    sleep 10
    
    docker-compose up -d fastapi
    print_status "Waiting for backend to be ready..."
    sleep 15
    
    docker-compose up -d frontend
    print_status "Waiting for frontend to be ready..."
    sleep 10
    
    docker-compose up -d nginx
    print_status "Starting nginx proxy..."
    sleep 5
    
    print_success "Services restarted"
}

# Main diagnostic and fix logic
main() {
    print_status "Starting NextAuth error diagnosis..."
    
    # Determine the base URL
    if [[ -n "$1" ]]; then
        BASE_URL="$1"
    else
        # Try to detect from environment or use default
        BASE_URL="http://206.189.89.239"
        if [[ -f ".env.production" ]]; then
            if grep -q "NEXTAUTH_URL" .env.production; then
                BASE_URL=$(grep "NEXTAUTH_URL" .env.production | cut -d'=' -f2)
            fi
        fi
    fi
    
    print_status "Using base URL: $BASE_URL"
    
    # Check main endpoints
    local main_healthy=true
    
    # Check nginx/main site
    if ! check_service_health "Main site" "$BASE_URL" "200"; then
        main_healthy=false
    fi
    
    # Check NextAuth session endpoint specifically
    if ! check_service_health "NextAuth session" "$BASE_URL/api/auth/session" "200"; then
        main_healthy=false
    fi
    
    # Check backend connectivity
    local backend_url="$BASE_URL"
    if ! check_backend_health "$backend_url"; then
        main_healthy=false
    fi
    
    if $main_healthy; then
        print_success "All services appear to be healthy!"
        print_status "The error might be intermittent. Monitor the logs for any recurring issues."
        return 0
    fi
    
    # If we have Docker, try to restart services
    if $DOCKER_AVAILABLE; then
        print_warning "Services are not healthy. Attempting to restart..."
        restart_docker_services
        
        # Wait for services to start
        print_status "Waiting for services to stabilize..."
        sleep 30
        
        # Re-check health
        if check_service_health "NextAuth session" "$BASE_URL/api/auth/session" "200"; then
            print_success "Services are now healthy after restart!"
        else
            print_error "Services are still not healthy after restart. Check logs:"
            echo "  docker-compose logs fastapi"
            echo "  docker-compose logs frontend"
            echo "  docker-compose logs nginx"
        fi
    else
        print_error "Manual intervention required:"
        echo "1. Check if backend service is running"
        echo "2. Check if frontend service is running"
        echo "3. Verify environment variables are set correctly"
        echo "4. Check network connectivity between services"
    fi
}

# Show usage if help requested
if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    echo "Usage: $0 [BASE_URL]"
    echo ""
    echo "Diagnoses and fixes NextAuth CLIENT_FETCH_ERROR issues"
    echo ""
    echo "Arguments:"
    echo "  BASE_URL    Base URL of your application (default: auto-detect)"
    echo ""
    echo "Examples:"
    echo "  $0                              # Auto-detect URL"
    echo "  $0 http://206.189.89.239       # Specific URL"
    echo "  $0 http://localhost             # Local development"
    exit 0
fi

# Run main function
main "$@"