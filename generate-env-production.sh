#!/bin/bash

# Generate secure random secrets
SECRET_KEY=$(openssl rand -hex 32)
NEXTAUTH_SECRET=$(openssl rand -hex 32) 
POSTGRES_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
REDIS_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
GRAFANA_ADMIN_PASSWORD=$(openssl rand -base64 16 | tr -d "=+/" | cut -c1-12)

# Create the production file with secure values
cat > .env.production << EOF
# Production Environment Configuration
# NextAuth.js configuration
NEXTAUTH_URL=http://206.189.89.239
NEXTAUTH_SECRET=${NEXTAUTH_SECRET}

# Backend configuration  
BACKEND_URL=http://fastapi:8000
NEXT_PUBLIC_BACKEND_URL=http://206.189.89.239/api/v1

# Database configuration
DATABASE_URL=postgresql://pm_user:${POSTGRES_PASSWORD}@pm_postgres_db:5432/pm_database
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

# Redis configuration
REDIS_PASSWORD=${REDIS_PASSWORD}

# Security keys
SECRET_KEY=${SECRET_KEY}

# Node environment
NODE_ENV=production

# Monitoring
GRAFANA_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD}

# Optional: SSL configuration
# SSL_CERT_PATH=/etc/nginx/ssl/cert.pem
# SSL_KEY_PATH=/etc/nginx/ssl/key.pem
EOF

echo "✅ Generated secure .env.production file with the following secrets:"
echo "🔑 SECRET_KEY: ${SECRET_KEY}"
echo "🔑 NEXTAUTH_SECRET: ${NEXTAUTH_SECRET}"
echo "🔑 POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}"
echo "🔑 REDIS_PASSWORD: ${REDIS_PASSWORD}"
echo "🔑 GRAFANA_ADMIN_PASSWORD: ${GRAFANA_ADMIN_PASSWORD}"
echo ""
echo "📁 File saved to: $(pwd)/.env.production"