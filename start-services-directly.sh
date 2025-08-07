#!/bin/bash

# Script to start services directly without Docker
# This will fix the nginx connection issues

set -e

echo "Starting services directly to fix nginx connection issues..."

# Create necessary directories
mkdir -p logs
mkdir -p uploads

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo "Port $port is already in use"
        return 1
    fi
    return 0
}

# Function to start backend
start_backend() {
    echo "Starting FastAPI backend..."
    cd backend
    
    # Install Python dependencies if not already installed
    if [ ! -d "venv" ]; then
        echo "Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    
    # Install requirements
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Set environment variables
    export DATABASE_URL="postgresql://pm_user:QlILLYN4kmmkuDzNwGrEsBQ4M@localhost:5432/pm_database"
    export REDIS_URL="redis://localhost:6379"
    export DEBUG="False"
    export LOG_LEVEL="WARNING"
    export SECRET_KEY="52b25338d9169462ec5fb249cf6ff05492c0e4c9a22b172c668bdbdaae112a5a"
    
    # Start FastAPI server
    echo "Starting FastAPI server on port 8000..."
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
    echo $! > ../logs/backend.pid
    
    cd ..
    echo "Backend started with PID $(cat logs/backend.pid)"
}

# Function to start frontend
start_frontend() {
    echo "Starting Next.js frontend..."
    cd frontend
    
    # Install Node.js dependencies if not already installed
    if [ ! -d "node_modules" ]; then
        echo "Installing Node.js dependencies..."
        npm install
    fi
    
    # Set environment variables
    export NODE_ENV="production"
    export NEXTAUTH_URL="http://206.189.89.239"
    export NEXTAUTH_SECRET="b9dc9437cd27ef4566cef5e97713b4de95e2f56bcb770ad272fc68d725bdb17b"
    export BACKEND_URL="http://localhost:8000"
    export NEXT_PUBLIC_BACKEND_URL="http://206.189.89.239/api/v1"
    
    # Build the application
    echo "Building Next.js application..."
    npm run build
    
    # Start Next.js server
    echo "Starting Next.js server on port 3000..."
    npm start &
    echo $! > ../logs/frontend.pid
    
    cd ..
    echo "Frontend started with PID $(cat logs/frontend.pid)"
}

# Function to start nginx
start_nginx() {
    echo "Starting nginx..."
    
    # Create a simple nginx configuration for direct mode
    cat > nginx/nginx-direct.conf << 'EOF'
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;
    
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;
    
    client_max_body_size 100M;
    
    upstream fastapi_backend {
        server 127.0.0.1:8000;
    }
    
    upstream nextjs_frontend {
        server 127.0.0.1:3000;
    }
    
    server {
        listen 80;
        server_name localhost _;
        
        # Health check
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
        
        # API routes
        location /api/ {
            proxy_pass http://fastapi_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Admin routes
        location /admin {
            proxy_pass http://fastapi_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # All other requests go to Next.js frontend
        location / {
            proxy_pass http://nextjs_frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
EOF
    
    # Start nginx with the new configuration
    if command -v nginx >/dev/null 2>&1; then
        sudo nginx -c $(pwd)/nginx/nginx-direct.conf &
        echo $! > logs/nginx.pid
        echo "Nginx started with PID $(cat logs/nginx.pid)"
    else
        echo "Warning: nginx not found. You may need to install it or use a different reverse proxy."
    fi
}

# Function to stop all services
stop_services() {
    echo "Stopping all services..."
    
    if [ -f "logs/backend.pid" ]; then
        kill $(cat logs/backend.pid) 2>/dev/null || true
        rm -f logs/backend.pid
    fi
    
    if [ -f "logs/frontend.pid" ]; then
        kill $(cat logs/frontend.pid) 2>/dev/null || true
        rm -f logs/frontend.pid
    fi
    
    if [ -f "logs/nginx.pid" ]; then
        sudo kill $(cat logs/nginx.pid) 2>/dev/null || true
        rm -f logs/nginx.pid
    fi
    
    echo "All services stopped."
}

# Main execution
case "$1" in
    start)
        echo "Starting all services..."
        
        # Check if ports are available
        check_port 8000 || exit 1
        check_port 3000 || exit 1
        check_port 80 || echo "Warning: Port 80 may be in use"
        
        start_backend
        sleep 5
        start_frontend
        sleep 5
        start_nginx
        
        echo "All services started successfully!"
        echo "- Frontend: http://localhost:3000"
        echo "- Backend API: http://localhost:8000"
        echo "- Nginx: http://localhost"
        ;;
    stop)
        stop_services
        ;;
    restart)
        stop_services
        sleep 2
        $0 start
        ;;
    status)
        echo "Service Status:"
        if [ -f "logs/backend.pid" ]; then
            echo "- Backend: Running (PID: $(cat logs/backend.pid))"
        else
            echo "- Backend: Not running"
        fi
        
        if [ -f "logs/frontend.pid" ]; then
            echo "- Frontend: Running (PID: $(cat logs/frontend.pid))"
        else
            echo "- Frontend: Not running"
        fi
        
        if [ -f "logs/nginx.pid" ]; then
            echo "- Nginx: Running (PID: $(cat logs/nginx.pid))"
        else
            echo "- Nginx: Not running"
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac