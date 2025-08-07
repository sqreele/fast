#!/bin/bash

# Quick fix for nginx connection issues
# This script updates the nginx configuration to use localhost instead of Docker container names

set -e

echo "Fixing nginx connection issues..."

# Backup the original nginx configuration
if [ -f "nginx/nginx.prod.conf" ]; then
    cp nginx/nginx.prod.conf nginx/nginx.prod.conf.backup
    echo "Backed up original nginx configuration"
fi

# Create a fixed nginx configuration that uses localhost
cat > nginx/nginx.prod.conf << 'EOF'
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    charset utf-8;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;
    error_log /var/log/nginx/error.log warn;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    keepalive_requests 100;
    types_hash_max_size 2048;
    server_tokens off;

    client_max_body_size 100M;
    client_body_buffer_size 1M;
    client_header_buffer_size 1k;
    large_client_header_buffers 4 8k;

    client_body_timeout 12;
    client_header_timeout 12;
    send_timeout 10;

    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
    proxy_buffer_size 4k;
    proxy_buffers 8 4k;
    proxy_busy_buffers_size 8k;
    proxy_temp_file_write_size 8k;

    # Upstream servers - using localhost instead of Docker container names
    upstream fastapi_backend {
        server 127.0.0.1:8000 max_fails=3 fail_timeout=30s;
        keepalive 32;
    }

    upstream nextjs_frontend {
        server 127.0.0.1:3000 max_fails=3 fail_timeout=30s;
        keepalive 32;
    }

    server {
        listen 80;
        server_name localhost _;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header Referrer-Policy "no-referrer-when-downgrade" always;
        add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

        client_max_body_size 100M;
        client_body_timeout 60s;

        # Health check endpoint
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }

        # NextAuth.js API routes
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
            
            proxy_hide_header X-Powered-By;
            add_header Cache-Control "no-cache, no-store, must-revalidate";
            
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Admin static files
        location /admin/statics/ {
            proxy_pass http://fastapi_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            expires 1d;
            add_header Cache-Control "public";
        }

        # Admin dashboard
        location /admin {
            proxy_pass http://fastapi_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            add_header Cache-Control "no-cache, no-store, must-revalidate";
            
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # API routes
        location /api/ {
            proxy_pass http://fastapi_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            proxy_buffering on;
            proxy_buffer_size 4k;
            proxy_buffers 8 4k;
            
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # WebSocket support
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

        # Static file uploads
        location /uploads/ {
            proxy_pass http://fastapi_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            expires 7d;
            add_header Cache-Control "public, no-transform";
        }

        # Next.js static assets
        location /_next/static/ {
            proxy_pass http://nextjs_frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # Static files
        location ~* "\.(ico|css|js|gif|jpe?g|png|svg|woff2?|ttf|eot)$" {
            proxy_pass http://nextjs_frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
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
            
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
            
            proxy_no_cache 1;
            proxy_cache_bypass 1;
            add_header Cache-Control "no-cache, no-store, must-revalidate";
            add_header Pragma "no-cache";
            add_header Expires "0";
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

echo "Nginx configuration updated to use localhost instead of Docker container names"
echo ""
echo "Next steps:"
echo "1. Start your backend service on port 8000"
echo "2. Start your frontend service on port 3000"
echo "3. Restart nginx with the new configuration"
echo ""
echo "To start services directly, run: ./start-services-directly.sh start"
echo "To check service status, run: ./start-services-directly.sh status"