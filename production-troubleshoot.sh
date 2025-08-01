#!/bin/bash

# Production Troubleshooting Script for PM System
# Run this script on your production server (206.189.89.239)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Server IP
SERVER_IP="206.189.89.239"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  PM System Production Troubleshooter  ${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to print status
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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Step 1: System Information
print_status "Step 1: Gathering system information..."
echo "Current user: $(whoami)"
echo "Current directory: $(pwd)"
echo "Server IP: $SERVER_IP"
echo "Date: $(date)"
echo ""

# Step 2: Check Docker Installation
print_status "Step 2: Checking Docker installation..."
if command_exists docker; then
    print_success "Docker is installed"
    docker --version
    
    # Check if Docker daemon is running
    if docker info >/dev/null 2>&1; then
        print_success "Docker daemon is running"
    else
        print_error "Docker daemon is not running"
        print_status "Attempting to start Docker..."
        sudo systemctl start docker || print_error "Failed to start Docker"
    fi
else
    print_error "Docker is not installed"
    exit 1
fi

if docker compose version >/dev/null 2>&1; then
    print_success "Docker Compose is installed"
    docker compose version
else
    print_error "Docker Compose is not installed"
    exit 1
fi
echo ""

# Step 3: Check Project Files
print_status "Step 3: Checking project files..."
required_files=("docker-compose.prod.yml" ".env.prod" "nginx/nginx.prod.conf")
missing_files=()

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        print_success "Found: $file"
    else
        print_error "Missing: $file"
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
    print_error "Missing required files. Please ensure all files are present."
    exit 1
fi
echo ""

# Step 4: Check Current Container Status
print_status "Step 4: Checking current container status..."
echo "Current running containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

echo "All containers (including stopped):"
docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo ""

# Step 5: Check Network Connectivity
print_status "Step 5: Checking network and firewall..."

# Check if ports are in use
echo "Checking port usage:"
for port in 80 443 3000 8000; do
    if ss -tulpn | grep ":$port " >/dev/null; then
        print_success "Port $port is in use"
        ss -tulpn | grep ":$port "
    else
        print_warning "Port $port is not in use"
    fi
done
echo ""

# Check firewall status
if command_exists ufw; then
    print_status "UFW Firewall status:"
    sudo ufw status
elif command_exists firewall-cmd; then
    print_status "Firewalld status:"
    sudo firewall-cmd --list-all
else
    print_warning "No known firewall management tool found"
fi
echo ""

# Step 6: Environment File Validation
print_status "Step 6: Validating environment configuration..."
if [ -f ".env.prod" ]; then
    echo "Environment file contents (sensitive values masked):"
    cat .env.prod | sed 's/\(PASSWORD\|SECRET\|KEY\)=.*/\1=***MASKED***/'
    echo ""
    
    # Check if NEXTAUTH_URL matches server IP
    if grep -q "NEXTAUTH_URL=http://$SERVER_IP" .env.prod; then
        print_success "NEXTAUTH_URL correctly configured for server IP"
    else
        print_warning "NEXTAUTH_URL might not match server IP"
        echo "Current NEXTAUTH_URL: $(grep NEXTAUTH_URL .env.prod)"
    fi
else
    print_error ".env.prod file not found"
fi
echo ""

# Step 7: Stop and Clean Previous Deployment
print_status "Step 7: Cleaning previous deployment..."
print_status "Stopping all containers..."
docker compose -f docker-compose.prod.yml down --remove-orphans || print_warning "Some containers were not running"

print_status "Removing unused Docker resources..."
docker system prune -f >/dev/null 2>&1 || true
echo ""

# Step 8: Build and Deploy
print_status "Step 8: Building and deploying services..."
print_status "Building images..."
if docker compose -f docker-compose.prod.yml build; then
    print_success "Images built successfully"
else
    print_error "Failed to build images"
    exit 1
fi

print_status "Starting services..."
if docker compose -f docker-compose.prod.yml --env-file .env.prod up -d; then
    print_success "Services started successfully"
else
    print_error "Failed to start services"
    exit 1
fi
echo ""

# Step 9: Wait for Services
print_status "Step 9: Waiting for services to initialize..."
sleep 30

# Check service status
print_status "Current service status:"
docker compose -f docker-compose.prod.yml ps
echo ""

# Step 10: Health Checks
print_status "Step 10: Performing health checks..."

# Check if nginx is running
if docker compose -f docker-compose.prod.yml ps nginx | grep -q "Up"; then
    print_success "Nginx container is running"
    
    # Test nginx configuration
    if docker compose -f docker-compose.prod.yml exec -T nginx nginx -t >/dev/null 2>&1; then
        print_success "Nginx configuration is valid"
    else
        print_error "Nginx configuration has errors"
        docker compose -f docker-compose.prod.yml exec -T nginx nginx -t
    fi
else
    print_error "Nginx container is not running"
    print_status "Nginx logs:"
    docker compose -f docker-compose.prod.yml logs nginx
fi

# Test internal connectivity
print_status "Testing internal service connectivity..."
if docker compose -f docker-compose.prod.yml exec -T nginx curl -s -f http://fastapi:8000/health >/dev/null 2>&1; then
    print_success "Nginx can reach FastAPI backend"
else
    print_warning "Nginx cannot reach FastAPI backend"
fi

if docker compose -f docker-compose.prod.yml exec -T nginx curl -s -f http://frontend:3000/ >/dev/null 2>&1; then
    print_success "Nginx can reach Frontend"
else
    print_warning "Nginx cannot reach Frontend"
fi

# Test local connectivity
print_status "Testing local connectivity..."
for endpoint in "/health" "/api/health" "/"; do
    if curl -s -f "http://localhost$endpoint" >/dev/null 2>&1; then
        print_success "Local endpoint $endpoint is accessible"
    else
        print_warning "Local endpoint $endpoint is not accessible"
    fi
done

# Test external connectivity
print_status "Testing external connectivity..."
for endpoint in "/health" "/api/health" "/"; do
    if curl -s -f "http://$SERVER_IP$endpoint" >/dev/null 2>&1; then
        print_success "External endpoint $endpoint is accessible"
    else
        print_warning "External endpoint $endpoint is not accessible"
    fi
done
echo ""

# Step 11: Port and Firewall Fix
print_status "Step 11: Ensuring firewall allows traffic..."
if command_exists ufw; then
    print_status "Configuring UFW firewall..."
    sudo ufw allow 80/tcp >/dev/null 2>&1
    sudo ufw allow 443/tcp >/dev/null 2>&1
    print_success "Firewall rules added for ports 80 and 443"
elif command_exists firewall-cmd; then
    print_status "Configuring firewalld..."
    sudo firewall-cmd --permanent --add-port=80/tcp >/dev/null 2>&1
    sudo firewall-cmd --permanent --add-port=443/tcp >/dev/null 2>&1
    sudo firewall-cmd --reload >/dev/null 2>&1
    print_success "Firewall rules added for ports 80 and 443"
fi
echo ""

# Step 12: Final Status Report
print_status "Step 12: Final status report..."
echo ""
echo "=== CONTAINER STATUS ==="
docker compose -f docker-compose.prod.yml ps
echo ""

echo "=== PORT MAPPINGS ==="
docker ps --format "table {{.Names}}\t{{.Ports}}" | grep -E "(nginx|fastapi|frontend)"
echo ""

echo "=== SERVICE LOGS (last 10 lines) ==="
for service in nginx fastapi frontend; do
    echo "--- $service ---"
    docker compose -f docker-compose.prod.yml logs --tail=10 $service 2>/dev/null || echo "Service $service not found"
    echo ""
done

# Step 13: Test URLs
print_status "Step 13: Testing application URLs..."
echo ""
echo "=== URL TESTING ==="

urls=(
    "http://localhost/health"
    "http://localhost/"
    "http://localhost/api/health"
    "http://$SERVER_IP/health"
    "http://$SERVER_IP/"
    "http://$SERVER_IP/api/health"
)

for url in "${urls[@]}"; do
    if curl -s -I "$url" | head -1 | grep -q "200\|301\|302"; then
        print_success "✅ $url - OK"
    else
        print_error "❌ $url - FAILED"
        echo "   Response: $(curl -s -I "$url" | head -1 2>/dev/null || echo 'No response')"
    fi
done
echo ""

# Step 14: Recommendations
print_status "Step 14: Recommendations and next steps..."
echo ""
echo "=== RECOMMENDATIONS ==="

# Check if all services are healthy
healthy_services=$(docker compose -f docker-compose.prod.yml ps | grep -c "Up.*healthy" || echo "0")
total_services=$(docker compose -f docker-compose.prod.yml ps | grep -c "Up" || echo "0")

if [ "$healthy_services" -eq "$total_services" ] && [ "$total_services" -gt 0 ]; then
    print_success "All services appear to be healthy!"
    echo ""
    echo "🌟 Your application should now be accessible at:"
    echo "   • Frontend: http://$SERVER_IP/"
    echo "   • API: http://$SERVER_IP/api/"
    echo "   • Health Check: http://$SERVER_IP/health"
    echo ""
else
    echo "⚠️  Some services may need attention:"
    echo ""
    echo "1. Check service logs for errors:"
    echo "   docker compose -f docker-compose.prod.yml logs [service_name]"
    echo ""
    echo "2. Restart problematic services:"
    echo "   docker compose -f docker-compose.prod.yml restart [service_name]"
    echo ""
    echo "3. Check nginx configuration:"
    echo "   docker compose -f docker-compose.prod.yml exec nginx nginx -t"
    echo ""
fi

echo "📋 Additional monitoring commands:"
echo "   • View all logs: docker compose -f docker-compose.prod.yml logs -f"
echo "   • Check status: docker compose -f docker-compose.prod.yml ps"
echo "   • Restart all: docker compose -f docker-compose.prod.yml restart"
echo "   • Stop all: docker compose -f docker-compose.prod.yml down"
echo ""

print_success "Troubleshooting complete!"
echo "Check the URLs above to verify your application is working."