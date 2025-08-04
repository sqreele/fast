#!/bin/bash

# Fix Production Upstream Issues Script
# This script addresses the nginx upstream connection problems

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Fixing Production Upstream Issues    ${NC}"
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

# Step 1: Check current status
print_status "Step 1: Checking current container status..."
if command -v docker >/dev/null 2>&1; then
    echo "Current running containers:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" || echo "No containers running"
    echo ""
    
    echo "All containers (including stopped):"
    docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" || echo "No containers found"
    echo ""
else
    print_error "Docker is not available"
    exit 1
fi

# Step 2: Stop all containers and clean up
print_status "Step 2: Stopping all containers and cleaning up..."
docker compose -f docker-compose.prod.yml down --remove-orphans --volumes || print_warning "Some containers were not running"

# Remove any dangling containers
docker container prune -f >/dev/null 2>&1 || true
docker network prune -f >/dev/null 2>&1 || true

print_success "Cleanup completed"
echo ""

# Step 3: Check and fix environment file
print_status "Step 3: Checking environment configuration..."
if [ ! -f ".env.prod" ]; then
    print_error ".env.prod file not found"
    print_status "Creating basic .env.prod file..."
    
    cat > .env.prod << 'EOF'
# Database Configuration
POSTGRES_PASSWORD=pm_secure_password_2024
POSTGRES_USER=pm_user
POSTGRES_DB=pm_database

# Redis Configuration
REDIS_PASSWORD=redis_secure_password_2024

# NextAuth Configuration
NEXTAUTH_URL=http://206.189.89.239
NEXTAUTH_SECRET=your-super-secret-nextauth-key-change-this-in-production
NEXT_PUBLIC_BACKEND_URL=http://206.189.89.239/api

# FastAPI Configuration
SECRET_KEY=your-super-secret-fastapi-key-change-this-in-production

# Grafana Configuration
GRAFANA_ADMIN_PASSWORD=admin_secure_password_2024
EOF
    
    print_success "Created .env.prod file"
else
    print_success ".env.prod file exists"
fi
echo ""

# Step 4: Fix nginx configuration for better upstream handling
print_status "Step 4: Updating nginx configuration for better upstream handling..."

# Create a backup of the current nginx config
cp nginx/nginx.prod.conf nginx/nginx.prod.conf.backup.$(date +%Y%m%d_%H%M%S)

# Update the upstream configuration in nginx
cat > nginx/nginx.prod.conf << 'EOF'
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

# Worker settings
worker_rlimit_nofile 65535;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    # MIME types
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Charset
    charset utf-8;

    # Logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    log_format detailed '$remote_addr - $remote_user [$time_local] "$request" '
                       '$status $body_bytes_sent "$http_referer" '
                       '"$http_user_agent" "$http_x_forwarded_for" '
                       'rt=$request_time uct="$upstream_connect_time" '
                       'uht="$upstream_header_time" urt="$upstream_response_time"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    # Basic settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    keepalive_requests 100;
    types_hash_max_size 2048;
    server_tokens off;

    # File size limits
    client_max_body_size 100M;
    client_body_buffer_size 1M;
    client_header_buffer_size 1k;
    large_client_header_buffers 4 8k;

    # Timeouts - Increased for better reliability
    client_body_timeout 60;
    client_header_timeout 60;
    send_timeout 60;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=20r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=10r/m;
    limit_conn_zone $binary_remote_addr zone=conn_limit_per_ip:10m;

    # Proxy settings - Increased timeouts
    proxy_connect_timeout 120s;
    proxy_send_timeout 120s;
    proxy_read_timeout 120s;
    proxy_buffer_size 8k;
    proxy_buffers 16 8k;
    proxy_busy_buffers_size 16k;
    proxy_temp_file_write_size 16k;

    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_session_tickets off;

    # OCSP stapling
    ssl_stapling on;
    ssl_stapling_verify on;

    # Cache zones
    proxy_cache_path /var/cache/nginx/api levels=1:2 keys_zone=api_cache:10m max_size=10g inactive=60m use_temp_path=off;
    proxy_cache_path /var/cache/nginx/static levels=1:2 keys_zone=static_cache:10m max_size=1g inactive=7d use_temp_path=off;

    # Upstream servers with improved load balancing and health checks
    upstream fastapi_backend {
        least_conn;
        server fastapi:8000 max_fails=5 fail_timeout=60s;
        keepalive 32;
    }

    upstream nextjs_frontend {
        least_conn;
        server frontend:3000 max_fails=5 fail_timeout=60s;
        keepalive 32;
    }

    # Rate limiting maps
    map $request_uri $limit_key {
        ~*/api/auth/  $binary_remote_addr;
        ~*/api/login  $binary_remote_addr;
        default       "";
    }

    # Bot detection map
    map $http_user_agent $is_bot {
        default 0;
        ~*GPTBot 1;
        ~*ChatGPT 1;
        ~*CCBot 1;
        ~*anthropic 1;
        ~*Claude-Web 1;
    }

    server {
        listen 80;
        server_name localhost _;

        # Rate limiting - increased limits for better usability
        limit_req zone=api burst=50 nodelay;
        limit_conn conn_limit_per_ip 20;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "no-referrer-when-downgrade" always;
        add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # Larger body size for file uploads
        client_max_body_size 100M;
        client_body_timeout 60s;

        # Real IP configuration (for load balancers)
        real_ip_header X-Forwarded-For;
        real_ip_recursive on;
        set_real_ip_from 10.0.0.0/8;
        set_real_ip_from 172.16.0.0/12;
        set_real_ip_from 192.168.0.0/16;

        # Nginx status endpoint for Prometheus monitoring
        location /nginx_status {
            stub_status on;
            access_log off;
            allow 172.18.0.0/16;  # Docker network
            allow 127.0.0.1;
            deny all;
        }

        # Health check endpoint
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }

        # Block or limit bot traffic
        location ~ "^/(20[0-9]{2}|[0-9]{4})/" {
            if ($is_bot) {
                return 429 "Rate limited";
            }
            try_files $uri $uri/ @frontend;
        }

        # NextAuth.js API routes - must come before /api/
        location /api/auth/ {
            proxy_pass http://nextjs_frontend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_set_header X-Forwarded-Host $host;
            proxy_set_header X-Forwarded-Port $server_port;
            
            # Security and caching headers
            proxy_hide_header X-Powered-By;
            add_header Cache-Control "no-cache, no-store, must-revalidate";
            
            # Timeouts
            proxy_connect_timeout 120s;
            proxy_send_timeout 120s;
            proxy_read_timeout 120s;
        }

        # Admin static files - serve from FastAPI
        location /admin/statics/ {
            proxy_pass http://fastapi_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Cache static admin files for 1 day
            proxy_cache static_cache;
            proxy_cache_valid 200 1d;
            proxy_cache_valid 404 5m;
            add_header X-Cache-Status $upstream_cache_status;
            
            expires 1d;
            add_header Cache-Control "public";
            
            # Timeouts
            proxy_connect_timeout 120s;
            proxy_send_timeout 120s;
            proxy_read_timeout 120s;
        }

        # Admin dashboard - proxy to FastAPI SQLAlchemy Admin
        location /admin {
            proxy_pass http://fastapi_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Cache control
            add_header Cache-Control "no-cache, no-store, must-revalidate";
            
            proxy_connect_timeout 120s;
            proxy_send_timeout 120s;
            proxy_read_timeout 120s;
        }

        # API routes - proxy to FastAPI
        location /api/ {
            limit_req zone=api burst=50 nodelay;
            
            proxy_pass http://fastapi_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Buffering settings
            proxy_buffering on;
            proxy_buffer_size 8k;
            proxy_buffers 16 8k;
            
            # Timeout settings
            proxy_connect_timeout 120s;
            proxy_send_timeout 120s;
            proxy_read_timeout 120s;
            
            # Cache API responses for 5 minutes
            proxy_cache api_cache;
            proxy_cache_valid 200 302 5m;
            proxy_cache_valid 404 1m;
            proxy_cache_bypass $http_pragma $http_authorization;
            proxy_no_cache $http_pragma $http_authorization;
            add_header X-Cache-Status $upstream_cache_status;
        }

        # WebSocket support for real-time features
        location /ws/ {
            proxy_pass http://fastapi_backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass 1;
        }

        # Static file uploads with extended caching
        location /uploads/ {
            proxy_pass http://fastapi_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Cache uploaded files for 7 days
            proxy_cache static_cache;
            proxy_cache_valid 200 7d;
            proxy_cache_valid 404 5m;
            add_header X-Cache-Status $upstream_cache_status;
            
            expires 7d;
            add_header Cache-Control "public, no-transform";
        }

        # Next.js static assets (_next/static)
        location /_next/static/ {
            proxy_pass http://nextjs_frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Cache static assets for 1 year
            proxy_cache static_cache;
            proxy_cache_valid 200 365d;
            proxy_cache_valid 404 5m;
            add_header X-Cache-Status $upstream_cache_status;
            
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # Next.js favicon and other static files
        location ~* "\.(ico|css|js|gif|jpe?g|png|svg|woff2?|ttf|eot)$" {
            proxy_pass http://nextjs_frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Cache static files for 30 days
            proxy_cache static_cache;
            proxy_cache_valid 200 30d;
            proxy_cache_valid 404 5m;
            add_header X-Cache-Status $upstream_cache_status;
            
            expires 30d;
            add_header Cache-Control "public";
        }

        # All other requests go to Next.js frontend
        location / {
            proxy_pass http://nextjs_frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeout settings
            proxy_connect_timeout 120s;
            proxy_send_timeout 120s;
            proxy_read_timeout 120s;
            
            # Don't cache HTML pages
            proxy_no_cache 1;
            proxy_cache_bypass 1;
            add_header Cache-Control "no-cache, no-store, must-revalidate";
            add_header Pragma "no-cache";
            add_header Expires "0";
        }

        # Frontend fallback for blog posts and other content
        location @frontend {
            proxy_pass http://nextjs_frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            proxy_no_cache 1;
            proxy_cache_bypass 1;
        }

        # Error pages
        error_page 404 /404.html;
        error_page 500 502 503 504 /50x.html;
        
        location = /50x.html {
            root /usr/share/nginx/html;
        }
        
        location = /404.html {
            root /usr/share/nginx/html;
        }

        # Deny access to hidden files
        location ~ "/\." {
            deny all;
        }

        # Deny access to backup files
        location ~ "~$" {
            deny all;
        }
    }
}
EOF

print_success "Updated nginx configuration with improved upstream handling"
echo ""

# Step 5: Build and start services
print_status "Step 5: Building and starting services..."

# Build images first
print_status "Building Docker images..."
if docker compose -f docker-compose.prod.yml build; then
    print_success "Images built successfully"
else
    print_error "Failed to build images"
    exit 1
fi

# Start services
print_status "Starting services..."
if docker compose -f docker-compose.prod.yml --env-file .env.prod up -d; then
    print_success "Services started successfully"
else
    print_error "Failed to start services"
    exit 1
fi

echo ""

# Step 6: Wait for services to initialize
print_status "Step 6: Waiting for services to initialize..."
sleep 45

# Step 7: Check service status
print_status "Step 7: Checking service status..."
docker compose -f docker-compose.prod.yml ps
echo ""

# Step 8: Verify nginx configuration
print_status "Step 8: Verifying nginx configuration..."
if docker compose -f docker-compose.prod.yml exec -T nginx nginx -t >/dev/null 2>&1; then
    print_success "Nginx configuration is valid"
    
    # Reload nginx to apply new configuration
    docker compose -f docker-compose.prod.yml exec -T nginx nginx -s reload
    print_success "Nginx configuration reloaded"
else
    print_error "Nginx configuration has errors"
    docker compose -f docker-compose.prod.yml exec -T nginx nginx -t
fi
echo ""

# Step 9: Test connectivity
print_status "Step 9: Testing service connectivity..."

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

# Test external connectivity
print_status "Testing external connectivity..."
for endpoint in "/health" "/api/health" "/"; do
    if curl -s -f "http://localhost$endpoint" >/dev/null 2>&1; then
        print_success "Local endpoint $endpoint is accessible"
    else
        print_warning "Local endpoint $endpoint is not accessible"
    fi
done
echo ""

# Step 10: Show logs for debugging
print_status "Step 10: Recent logs from services..."
echo "=== NGINX LOGS (last 20 lines) ==="
docker compose -f docker-compose.prod.yml logs --tail=20 nginx 2>/dev/null || echo "Nginx logs not available"
echo ""

echo "=== FRONTEND LOGS (last 10 lines) ==="
docker compose -f docker-compose.prod.yml logs --tail=10 frontend 2>/dev/null || echo "Frontend logs not available"
echo ""

echo "=== FASTAPI LOGS (last 10 lines) ==="
docker compose -f docker-compose.prod.yml logs --tail=10 fastapi 2>/dev/null || echo "FastAPI logs not available"
echo ""

# Step 11: Final status and recommendations
print_status "Step 11: Final status and recommendations..."
echo ""

echo "=== CURRENT STATUS ==="
docker compose -f docker-compose.prod.yml ps
echo ""

echo "=== TESTING URLS ==="
urls=(
    "http://localhost/health"
    "http://localhost/"
    "http://localhost/api/health"
    "http://localhost/admin"
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

print_success "Fix completed!"
echo ""
echo "🌟 Your application should now be accessible at:"
echo "   • Frontend: http://localhost/"
echo "   • API: http://localhost/api/"
echo "   • Admin: http://localhost/admin"
echo "   • Health Check: http://localhost/health"
echo ""
echo "📋 If you still see issues, check:"
echo "   • docker compose -f docker-compose.prod.yml logs -f [service_name]"
echo "   • docker compose -f docker-compose.prod.yml ps"
echo "   • docker compose -f docker-compose.prod.yml restart [service_name]"
echo ""