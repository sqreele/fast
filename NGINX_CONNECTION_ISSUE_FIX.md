# Nginx Connection Issue Fix

## Problem Analysis

The nginx logs showed the following errors:

```
pm_nginx  | 2025/08/07 03:11:41 [error] 8#8: *5 connect() failed (111: Connection refused) while connecting to upstream, client: 161.82.166.238, server: localhost, request: "GET / HTTP/1.1", upstream: "http://172.18.0.10:3000/", host: "206.189.89.239"
pm_nginx  | 2025/08/07 03:11:41 [error] 8#8: *5 connect() failed (111: Connection refused) while connecting to upstream, client: 161.82.166.238, server: localhost, request: "GET / HTTP/1.1", upstream: "http://172.18.0.9:3000/", host: "206.189.89.239"
pm_nginx  | 2025/08/07 03:12:02 [error] 8#8: *5 no live upstreams while connecting to upstream, client: 161.82.166.238, server: localhost, request: "GET / HTTP/1.1", upstream: "http://nextjs_frontend/", host: "206.189.89.239"
```

### Root Cause

1. **Docker containers not running**: The nginx configuration was trying to connect to Docker containers that were not active
2. **Wrong upstream configuration**: The nginx config was using Docker container names (`nextjs_frontend`, `fastapi`) and IPs (`172.18.0.9:3000`, `172.18.0.10:3000`) instead of localhost
3. **Service dependency issues**: The frontend and backend services were not running, causing nginx to fail with 502 Bad Gateway errors

## Solution Implemented

### 1. Fixed Nginx Configuration

Updated `nginx/nginx.prod.conf` to use localhost instead of Docker container names:

```nginx
# Before (Docker container names)
upstream nextjs_frontend {
    server frontend:3000 max_fails=3 fail_timeout=30s;
    keepalive 32;
}

# After (localhost)
upstream nextjs_frontend {
    server 127.0.0.1:3000 max_fails=3 fail_timeout=30s;
    keepalive 32;
}
```

### 2. Created Service Management Scripts

#### `fix-nginx-connection.sh`
- Updates nginx configuration to use localhost
- Backs up original configuration
- Provides clear next steps

#### `start-services-directly.sh`
- Starts services directly without Docker
- Manages Python virtual environment
- Installs dependencies automatically
- Provides service management commands

## Usage Instructions

### Quick Fix (Recommended)

1. **Apply the nginx fix**:
   ```bash
   ./fix-nginx-connection.sh
   ```

2. **Start services directly**:
   ```bash
   ./start-services-directly.sh start
   ```

3. **Check service status**:
   ```bash
   ./start-services-directly.sh status
   ```

### Service Management Commands

```bash
# Start all services
./start-services-directly.sh start

# Stop all services
./start-services-directly.sh stop

# Restart all services
./start-services-directly.sh restart

# Check service status
./start-services-directly.sh status
```

## Service Ports

- **Frontend (Next.js)**: Port 3000
- **Backend (FastAPI)**: Port 8000
- **Nginx**: Port 80

## Environment Configuration

The services use the following environment variables from `.env.prod`:

- `NEXTAUTH_URL=http://206.189.89.239`
- `NEXTAUTH_SECRET=b9dc9437cd27ef4566cef5e97713b4de95e2f56bcb770ad272fc68d725bdb17b`
- `DATABASE_URL=postgresql://pm_user:QlILLYN4kmmkuDzNwGrEsBQ4M@localhost:5432/pm_database`
- `SECRET_KEY=52b25338d9169462ec5fb249cf6ff05492c0e4c9a22b172c668bdbdaae112a5a`

## Verification Steps

1. **Check if services are running**:
   ```bash
   ./start-services-directly.sh status
   ```

2. **Test nginx health endpoint**:
   ```bash
   curl http://localhost/health
   ```

3. **Test frontend**:
   ```bash
   curl http://localhost:3000
   ```

4. **Test backend**:
   ```bash
   curl http://localhost:8000/health
   ```

## Troubleshooting

### If services fail to start:

1. **Check port availability**:
   ```bash
   lsof -i :3000
   lsof -i :8000
   lsof -i :80
   ```

2. **Check logs**:
   ```bash
   tail -f logs/backend.log
   tail -f logs/frontend.log
   ```

3. **Install missing dependencies**:
   ```bash
   # For backend
   cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
   
   # For frontend
   cd frontend && npm install
   ```

### If nginx still shows connection errors:

1. **Verify services are running on correct ports**
2. **Check nginx configuration syntax**:
   ```bash
   sudo nginx -t -c $(pwd)/nginx/nginx.prod.conf
   ```
3. **Restart nginx with new configuration**

## Alternative: Docker Solution

If you prefer to use Docker:

1. **Install Docker** (if not already installed):
   ```bash
   sudo ./get-docker.sh
   ```

2. **Start Docker daemon**:
   ```bash
   sudo service docker start
   ```

3. **Start production services**:
   ```bash
   sudo ./docker-manage.sh prod
   ```

## Files Modified

- `nginx/nginx.prod.conf` - Updated upstream configuration
- `nginx/nginx.prod.conf.backup` - Original configuration backup
- `fix-nginx-connection.sh` - Quick fix script
- `start-services-directly.sh` - Service management script

## Expected Results

After applying the fix:

- ✅ Nginx will connect to localhost services instead of Docker containers
- ✅ 502 Bad Gateway errors will be resolved
- ✅ Services will be accessible via nginx proxy
- ✅ Health checks will return "healthy" status
- ✅ Frontend and backend will communicate properly

## Security Notes

- The configuration includes security headers
- Rate limiting is configured for API endpoints
- Static files are properly cached
- Admin routes are protected
- Hidden files are denied access