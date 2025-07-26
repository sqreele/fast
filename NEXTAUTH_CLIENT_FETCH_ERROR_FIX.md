# NextAuth CLIENT_FETCH_ERROR Fix

## Problem
The error `[next-auth][error][CLIENT_FETCH_ERROR] "Unexpected token 'S', "Server error" is not valid JSON"` occurs when NextAuth receives a non-JSON response from the authentication endpoint. This commonly happens with **503 Service Temporarily Unavailable** errors.

## Root Causes Identified and Fixed

### 1. **503 Service Temporarily Unavailable** ✅ NEW FIX
**Issue**: Backend FastAPI service is temporarily unreachable, causing nginx to return HTML error pages instead of JSON.

**Root Causes**:
- Docker container startup race conditions
- Backend service crashes or restarts
- Network connectivity issues between frontend and backend
- Missing or incorrect health checks

**Fix Applied**:
- Enhanced Docker Compose health checks and dependencies
- Added timeout and retry logic to NextAuth provider
- Improved service startup order
- Created diagnostic script (`fix-nextauth-error.sh`)

### 2. **Incorrect SignIn Page Configuration** ✅ FIXED
**Issue**: The signin page was incorrectly configured in NextAuth configuration as `/api/auth/signin`, which conflicts with NextAuth's internal API routes.

**Fix Applied**:
- Updated `frontend/src/app/api/auth/[...nextauth]/route.ts` signin page path from `/api/auth/signin` to `/signin`
- Created new signin page at `frontend/src/app/signin/page.tsx`
- Removed the incorrectly placed signin page from `frontend/src/app/api/auth/signin/`

### 3. **Enhanced Error Handling in NextAuth Provider** ✅ ENHANCED
**Issue**: Poor error handling when backend returns non-JSON responses.

**Fix Applied**:
- Added content-type checking before parsing responses
- Enhanced error handling for network issues
- Added detailed logging for debugging
- **NEW**: Added request timeout handling (10 seconds)
- **NEW**: Added abort controller for better error handling
- **NEW**: Enhanced network error detection

### 4. **Missing CORS Configuration** ✅ FIXED
**Issue**: Backend was missing CORS middleware, causing requests from Next.js to be blocked.

**Fix Applied**:
- Added CORS middleware to `backend/main.py`
- Configured allowed origins for development and production

### 5. **Environment Configuration** ✅ ENHANCED
**Issue**: Missing or incorrect environment variables.

**Fix Applied**:
- Created `frontend/.env.local.example` with proper NextAuth configuration
- Ensured `NEXTAUTH_SECRET`, `NEXTAUTH_URL`, and `BACKEND_URL` are properly set
- **NEW**: Updated production environment for IP `206.189.89.239`
- **NEW**: Fixed `NEXTAUTH_URL` and `NEXT_PUBLIC_BACKEND_URL` for production

### 6. **Docker Service Dependencies** ✅ NEW FIX
**Issue**: Services starting in wrong order causing temporary unavailability.

**Fix Applied**:
- Enhanced `docker-compose.yml` with proper health check dependencies
- Increased health check timeouts and retries
- Improved service startup sequence

## Quick Fix Script

Run the diagnostic and fix script:

```bash
./fix-nextauth-error.sh
```

Or for a specific URL:
```bash
./fix-nextauth-error.sh http://206.189.89.239
```

This script will:
- Check service health endpoints
- Diagnose connectivity issues
- Restart services in correct order if needed
- Provide specific error guidance

## Manual Fixes

### For Production Deployment (IP: 206.189.89.239)

1. **Update environment variables**:
   ```bash
   cp .env.production .env
   # Edit .env to ensure:
   NEXTAUTH_URL=http://206.189.89.239
   NEXT_PUBLIC_BACKEND_URL=http://206.189.89.239/api/v1
   ```

2. **Restart services in correct order**:
   ```bash
   docker-compose stop nginx frontend fastapi
   docker-compose up -d fastapi
   sleep 30  # Wait for backend to be ready
   docker-compose up -d frontend
   sleep 15  # Wait for frontend to be ready
   docker-compose up -d nginx
   ```

### For Development

```bash
cd frontend
npm run dev
```

And in another terminal:
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Configuration Files Updated

### Enhanced NextAuth Configuration (`frontend/src/app/api/auth/[...nextauth]/route.ts`)
```typescript
// Key improvements:
1. Added 10-second timeout with AbortController
2. Enhanced error handling for timeout scenarios
3. Better network error detection
4. Added NextAuth event handlers for debugging
```

### Enhanced Docker Compose (`docker-compose.yml`)
```yaml
# Key improvements:
1. Better health check dependencies
2. Longer startup periods (60 seconds)
3. More retries for health checks
4. Proper service dependency order
```

### Production Environment (`.env.production`)
```env
# Updated for current deployment:
NEXTAUTH_URL=http://206.189.89.239
NEXT_PUBLIC_BACKEND_URL=http://206.189.89.239/api/v1
```

## Troubleshooting Steps

### If Still Getting 503 Errors:

1. **Check service status**:
   ```bash
   curl -I http://206.189.89.239/health
   curl -I http://206.189.89.239/api/auth/session
   ```

2. **Check Docker logs**:
   ```bash
   docker-compose logs fastapi
   docker-compose logs frontend
   docker-compose logs nginx
   ```

3. **Verify backend connectivity**:
   ```bash
   # From inside the frontend container:
   curl http://fastapi:8000/health
   ```

### If Backend is Not Responding:

1. **Restart backend service**:
   ```bash
   docker-compose restart fastapi
   ```

2. **Check backend health**:
   ```bash
   curl http://206.189.89.239/docs
   ```

3. **Check database connectivity**:
   ```bash
   docker-compose logs pm_postgres_db
   ```

## Common Error Patterns

### "Server error\n" Response
- **Cause**: nginx returning HTML error page instead of JSON
- **Fix**: Restart backend service, check health endpoints

### 503 Service Temporarily Unavailable
- **Cause**: Backend service is down or unreachable
- **Fix**: Use the diagnostic script or restart services manually

### Timeout Errors
- **Cause**: Backend taking too long to respond
- **Fix**: Check backend performance, database connections

## Verification Checklist

- [ ] Backend service starts without errors
- [ ] Frontend service starts without errors  
- [ ] CORS middleware is enabled on backend
- [ ] Environment variables are properly set for production IP
- [ ] NextAuth session endpoint returns `{}` (empty JSON object)
- [ ] No CLIENT_FETCH_ERROR in browser console
- [ ] Authentication flow completes successfully
- [ ] Services start in correct dependency order

## Prevention

1. **Monitor health endpoints regularly**
2. **Set up proper logging and alerting**
3. **Use the diagnostic script in CI/CD pipelines**
4. **Implement graceful service restarts**
5. **Monitor backend response times**

If you continue to experience issues after applying these fixes, run the diagnostic script first, then check the specific error logs as directed.