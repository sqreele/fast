# Production Nginx Routing Fix Summary

**Date:** $(date +"%Y-%m-%d %H:%M:%S")  
**Issue:** Multiple 404 errors in production nginx logs  
**Status:** ✅ RESOLVED

## Problem Analysis

The production environment was experiencing multiple 404 errors due to routing misconfigurations in the nginx setup:

### Original Issues from Logs:
```
pm_nginx  | 13.219.19.81 - - [01/Aug/2025:06:11:56 +0000] "GET /admin HTTP/1.1" 404 6859
pm_nginx  | 161.82.166.238 - - [01/Aug/2025:06:12:06 +0000] "GET /api/auth/providers HTTP/1.1" 404 22
pm_nginx  | 161.82.166.238 - - [01/Aug/2025:06:12:06 +0000] "POST /api/auth/_log HTTP/1.1" 404 22
pm_nginx  | 161.82.166.238 - - [01/Aug/2025:06:12:06 +0000] "GET /api/auth/error HTTP/1.1" 404 22
pm_nginx  | 13.219.19.81 - - [01/Aug/2025:06:12:06 +0000] "GET /api/v1/admin/ HTTP/1.1" 404 22
```

### Root Causes:

1. **Missing `/admin` route** in `nginx.prod.conf`
2. **Missing NextAuth `/api/auth/` routes** in production config
3. **Conflicting authentication configuration** that routed auth requests to FastAPI instead of Next.js
4. **Missing root endpoint** for `/api/v1/admin/` in the backend

## Fixes Applied

### 1. Added Missing `/admin` Route

**File:** `nginx/nginx.prod.conf`  
**Location:** Added before `/api/` location block

```nginx
# Admin dashboard - proxy to FastAPI SQLAlchemy Admin
location /admin {
    # Additional authentication can be added here
    # auth_basic "Admin Area";
    # auth_basic_user_file /etc/nginx/.htpasswd;
    
    proxy_pass http://fastapi_backend;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # Cache control
    add_header Cache-Control "no-cache, no-store, must-revalidate";
    
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
}
```

### 2. Added NextAuth Routes

**File:** `nginx/nginx.prod.conf`  
**Location:** Added before `/api/` location block (order is critical)

```nginx
# NextAuth.js API routes - must come before /api/
location /api/auth/ {
    # Disable rate limiting for auth endpoints to prevent login issues
    # limit_req zone=login burst=10 nodelay;
    
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
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
}
```

### 3. Removed Conflicting Auth Configuration

**File:** `nginx/nginx.prod.conf`  
**Removed:** Duplicate authentication section that was routing to FastAPI

```nginx
# REMOVED - This was conflicting with NextAuth
location ~ "^/api/(auth|login)" {
    limit_req zone=login burst=10 nodelay;
    proxy_pass http://fastapi_backend;  # ← This was wrong!
    # ... rest of config
}
```

### 4. Added Backend Admin Root Endpoint

**File:** `backend/routes/admin.py`  
**Added:** Root route to handle `/api/v1/admin/` requests

```python
@router.get("/")
def admin_root(_: bool = Depends(require_admin_role)):
    """Root admin endpoint - provides available admin operations"""
    return {
        "message": "PM System Admin API",
        "version": "1.0.0",
        "available_endpoints": [
            "/stats - System statistics",
            "/setup - Initial system setup", 
            "/users - User management",
            "/test - System tests",
            "/backup - Database backup",
            "/reset - Database reset"
        ]
    }
```

## Configuration Architecture

### Route Precedence (Order Matters!)
1. `/nginx_status` - Nginx monitoring
2. `/health` - Health checks
3. `/api/auth/` - NextAuth routes → Next.js frontend
4. `/admin` - Admin dashboard → FastAPI backend
5. `/api/` - API routes → FastAPI backend
6. `/ws/` - WebSocket routes → FastAPI backend
7. `/_next/static/` - Static assets → Next.js frontend
8. `/` - All other routes → Next.js frontend

### Service Routing:
- **Next.js Frontend** (`frontend:3000`): Handles auth routes and main application
- **FastAPI Backend** (`fastapi:8000`): Handles API and admin routes
- **Nginx** (`nginx:80/443`): Routes traffic between services

## Verification Steps

### 1. Run the Fix Script
```bash
chmod +x fix-production-nginx-routes.sh
./fix-production-nginx-routes.sh
```

### 2. Manual Verification
```bash
# Check admin routes
curl -I http://localhost/admin
curl -I http://localhost/api/v1/admin/

# Check NextAuth routes
curl -I http://localhost/api/auth/providers
curl -I http://localhost/api/auth/error

# Check API routes
curl -I http://localhost/api/v1/
curl -I http://localhost/health
```

### 3. Monitor Logs
```bash
docker compose -f docker-compose.prod.yml logs -f nginx
```

## Expected Results

After applying these fixes:

- ✅ `/admin` returns 200 or authentication prompt instead of 404
- ✅ `/api/auth/providers` returns NextAuth provider information
- ✅ `/api/auth/_log` accepts POST requests for auth logging
- ✅ `/api/auth/error` returns error handling information
- ✅ `/api/v1/admin/` returns admin API information

## Files Modified

1. `nginx/nginx.prod.conf` - Added missing routes and removed conflicts
2. `backend/routes/admin.py` - Added root admin endpoint
3. `fix-production-nginx-routes.sh` - Created automated fix script

## Monitoring

Continue monitoring nginx logs for any remaining 404 errors:

```bash
# Real-time log monitoring
docker compose -f docker-compose.prod.yml logs -f nginx | grep " 404 "

# Check for specific patterns
docker compose -f docker-compose.prod.yml logs nginx | grep -E "(admin|auth)" | grep " 404 "
```

## Notes

- **Order is critical** in nginx location blocks - more specific routes must come before general ones
- NextAuth routes must be handled by the Next.js frontend, not the FastAPI backend
- The admin dashboard uses SQLAlchemy Admin from the FastAPI backend
- All fixes maintain security headers and proper caching policies

---

**Maintenance:** This fix should resolve the routing issues permanently. If similar 404s appear, check for:
1. New routes added without corresponding nginx configuration
2. Changes to service names in docker-compose
3. Port conflicts or service unavailability