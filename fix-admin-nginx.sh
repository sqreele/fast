#!/bin/bash

# Fix for PM System Admin Interface Access
# This script applies the nginx configuration fix and restarts the nginx container

set -e

echo "=== PM System Admin Interface Fix ==="
echo "Server: 206.189.89.239"
echo "Date: $(date)"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Step 1: Check Docker status
print_status "Step 1: Checking Docker status..."
if ! command -v docker &> /dev/null; then
    print_error "Docker not found. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    systemctl start docker
    systemctl enable docker
    print_success "Docker installed and started"
else
    print_success "Docker is available"
fi

# Step 2: Check running containers
print_status "Step 2: Checking running containers..."
docker ps -a | grep -E "(nginx|fastapi|frontend)" || print_warning "No containers found with nginx/fastapi/frontend names"

# Step 3: Check if production services are running
print_status "Step 3: Checking production services..."
if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    print_success "Production services are running"
    
    # Step 4: Restart nginx to apply configuration changes
    print_status "Step 4: Restarting nginx to apply admin route configuration..."
    docker-compose -f docker-compose.prod.yml restart nginx || docker-compose -f docker-compose.prod.yml restart proxy || print_warning "Could not restart nginx service"
    
    # Wait for nginx to restart
    sleep 10
    
    # Step 5: Test admin interface
    print_status "Step 5: Testing admin interface access..."
    
    if curl -s -f http://206.189.89.239/admin/ > /dev/null 2>&1; then
        print_success "Admin interface is now accessible at http://206.189.89.239/admin/"
    else
        print_warning "Admin interface still not accessible. Checking backend connectivity..."
        
        # Check if backend is running
        if docker-compose -f docker-compose.prod.yml ps | grep -q "fastapi.*Up"; then
            print_success "FastAPI backend is running"
        else
            print_error "FastAPI backend is not running"
            print_status "Starting FastAPI backend..."
            docker-compose -f docker-compose.prod.yml up -d fastapi
        fi
    fi
    
else
    print_warning "Production services are not running. Starting them..."
    
    # Check if .env.prod exists
    if [ -f ".env.prod" ]; then
        print_status "Starting production services..."
        docker-compose -f docker-compose.prod.yml up -d
        sleep 30
        
        print_status "Testing admin interface after startup..."
        if curl -s -f http://206.189.89.239/admin/ > /dev/null 2>&1; then
            print_success "Admin interface is now accessible at http://206.189.89.239/admin/"
        else
            print_error "Admin interface is still not accessible"
        fi
    else
        print_error ".env.prod file not found. Cannot start production services."
        print_status "Please create .env.prod file and run: ./deploy-production.sh"
    fi
fi

# Step 6: Provide troubleshooting information
print_status "Step 6: Admin Interface Access Information"
echo ""
echo "=== Admin Interface Access ==="
echo "URL: http://206.189.89.239/admin/"
echo "Note: The admin interface is SQLAlchemy Admin mounted on FastAPI"
echo ""
echo "=== Troubleshooting ==="
echo "1. Check if backend is accessible: curl http://206.189.89.239/api/"
echo "2. Check container logs: docker-compose -f docker-compose.prod.yml logs nginx fastapi"
echo "3. Check nginx configuration: docker exec <nginx_container> nginx -t"
echo "4. Restart all services: docker-compose -f docker-compose.prod.yml restart"
echo ""
echo "=== Expected Admin Features ==="
echo "- User Management"
echo "- Property Management" 
echo "- Room & Machine Management"
echo "- Work Orders & Maintenance"
echo "- PM Schedules & Inspections"
echo "- File Management"
echo ""

print_status "Fix script completed. Check the admin interface at http://206.189.89.239/admin/"