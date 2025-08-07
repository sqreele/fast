# Profile Loading Troubleshooting Guide

## Issue: "Failed to load profile" Error

This error occurs when the frontend application cannot successfully load user profile data from the backend API.

## Common Causes and Solutions

### 1. Backend Service Not Running

**Symptoms:**
- "Failed to load profile" error message
- Network error in browser console
- API calls returning connection refused errors

**Solution:**
```bash
# Start the backend service
cd backend
source venv/bin/activate
python3 main.py
```

**Or use the automated script:**
```bash
./start-services.sh
```

### 2. Frontend Service Not Running

**Symptoms:**
- Application not accessible at http://localhost:3000
- "This site can't be reached" error

**Solution:**
```bash
# Start the frontend service
cd frontend
npm install  # If dependencies not installed
npm run dev
```

### 3. Environment Configuration Issues

**Symptoms:**
- API calls failing with wrong URLs
- Authentication issues

**Check your `.env` file:**
```bash
# Ensure these variables are set correctly
NEXTAUTH_URL=http://localhost
BACKEND_URL=http://fastapi:8000  # For Docker
# or
BACKEND_URL=http://localhost:8000  # For local development
NEXT_PUBLIC_BACKEND_URL=http://localhost/api/v1
```

### 4. Database Connection Issues

**Symptoms:**
- Backend starts but API calls fail
- Database connection errors in backend logs

**Solution:**
- Ensure PostgreSQL is running
- Check database credentials in `.env` file
- Verify DATABASE_URL format (no line breaks)

### 5. Authentication Issues

**Symptoms:**
- 401 Unauthorized errors
- Session not persisting

**Solution:**
- Clear browser cache and cookies
- Sign out and sign back in
- Check NextAuth configuration

## Quick Diagnostic Steps

### 1. Check Service Status
```bash
# Check if services are running
ps aux | grep -E "(node|python|fastapi)" | grep -v grep

# Check if ports are in use
netstat -tulpn | grep -E "(3000|8000)"
```

### 2. Test API Endpoints
```bash
# Test backend health
curl http://localhost:8000/health

# Test profile endpoint (requires authentication)
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/v1/auth/me
```

### 3. Check Browser Console
- Open browser developer tools (F12)
- Go to Console tab
- Look for error messages when loading profile page

### 4. Check Network Tab
- Open browser developer tools (F12)
- Go to Network tab
- Reload the profile page
- Look for failed API requests

## Automated Fixes

### Use the Start Services Script
```bash
./start-services.sh
```

This script will:
- Check if Docker is available
- Start services with Docker Compose if available
- Otherwise, start services manually
- Install dependencies if needed
- Provide status updates

### Manual Service Startup

**Backend:**
```bash
cd backend
source venv/bin/activate
pip install --break-system-packages -r requirements.txt
python3 main.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Environment-Specific Solutions

### Docker Environment
```bash
# Start all services
docker-compose up -d

# Check service logs
docker-compose logs -f

# Restart specific service
docker-compose restart backend
```

### Local Development Environment
```bash
# Start backend
cd backend && source venv/bin/activate && python3 main.py &

# Start frontend
cd frontend && npm run dev &
```

## Prevention

1. **Always use the start script:** `./start-services.sh`
2. **Check service status before accessing the application**
3. **Monitor logs for early error detection**
4. **Keep dependencies updated**

## Getting Help

If the issue persists after trying these solutions:

1. Check the application logs for detailed error messages
2. Verify all environment variables are set correctly
3. Ensure all required services (PostgreSQL, Redis) are running
4. Try clearing browser cache and cookies
5. Restart all services

## Recent Fixes Applied

- ✅ Fixed DATABASE_URL line break issue in `.env` file
- ✅ Improved error handling in profile page
- ✅ Enhanced error messages for better user feedback
- ✅ Added retry mechanism with better UI
- ✅ Created automated service startup script
- ✅ Improved axios error handling for network issues