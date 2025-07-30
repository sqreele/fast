# Deployment Fixes for FastAPI Authentication and Dependency Issues

## Issues Identified

### 1. Database Authentication Failure
**Error:** `FATAL: password authentication failed for user "pm_user"`

**Root Causes:**
- Inconsistent password configuration between containers
- PostgreSQL authentication method restrictions (scram-sha-256)
- Environment variable mismatches

### 2. Missing Starlette Dependency
**Error:** `ModuleNotFoundError: No module named 'starlette'`

**Root Causes:**
- Starlette not explicitly listed in requirements.txt
- Dockerfile using `--no-deps` flag preventing transitive dependency installation
- FastAPI requires starlette but it wasn't being installed

## Fixes Applied

### 1. Fixed Requirements.txt
- **Added:** `starlette==0.41.2` explicitly to requirements.txt
- **Reason:** FastAPI depends on starlette, but it wasn't being installed due to Docker configuration

### 2. Updated Dockerfile
- **Changed:** Removed `--no-deps` flag from pip install command
- **Before:** `pip install --no-deps -r requirements.txt`
- **After:** `pip install -r requirements.txt`
- **Reason:** `--no-deps` was preventing installation of transitive dependencies like starlette

### 3. Database Authentication Fix
- **Removed:** PostgreSQL authentication restrictions that were causing issues
- **Changed:** Commented out `POSTGRES_INITDB_ARGS` and `POSTGRES_HOST_AUTH_METHOD` in production config
- **Added:** Better environment variable management with `.env.prod` file

### 4. Environment Configuration
- **Created:** `.env.prod` file with consistent environment variables
- **Ensured:** Database credentials match between all services
- **Added:** Better logging to debug connection issues

### 5. Deployment Scripts
- **Created:** `deploy-production.sh` - Production deployment with environment file support
- **Created:** `deploy-dev.sh` - Development deployment for easier debugging

## How to Deploy

### Development Deployment
```bash
./deploy-dev.sh
```

### Production Deployment
1. Review and update `.env.prod` with your production values:
   ```bash
   # Update secret keys, passwords, etc.
   nano .env.prod
   ```

2. Run the production deployment:
   ```bash
   ./deploy-production.sh
   ```

## Environment Variables

### Required Production Variables (.env.prod)
```bash
# Database
POSTGRES_PASSWORD=your-secure-password
DATABASE_URL=postgresql://pm_user:your-secure-password@pm_postgres_db:5432/pm_database

# Application
SECRET_KEY=your-production-secret-key
DEBUG=False
WORKERS=4

# NextAuth
NEXTAUTH_SECRET=your-nextauth-secret
NEXTAUTH_URL=https://yourdomain.com
```

## Verification Steps

1. **Check container status:**
   ```bash
   docker-compose -f docker-compose.prod.yml ps
   ```

2. **View application logs:**
   ```bash
   docker-compose -f docker-compose.prod.yml logs -f fastapi
   ```

3. **Test database connection:**
   ```bash
   docker-compose -f docker-compose.prod.yml exec fastapi python -c "from database import engine; engine.connect()"
   ```

4. **Test API health:**
   ```bash
   curl http://localhost/api/v1/health
   ```

## Troubleshooting

### If containers still fail to start:
1. Check environment variables are properly loaded
2. Ensure all secret keys are properly set
3. Verify database credentials match between services
4. Check Docker logs for specific error messages

### If database authentication still fails:
1. Verify PostgreSQL container is using the correct password
2. Check that the FastAPI container has the same credentials
3. Consider recreating the database volume:
   ```bash
   docker-compose -f docker-compose.prod.yml down -v
   docker-compose -f docker-compose.prod.yml up --build
   ```

## Security Notes

- Always change default passwords in production
- Use strong, unique secret keys
- Consider using Docker secrets for sensitive data
- Regularly update dependency versions for security patches

## File Changes Summary

1. `backend/requirements.txt` - Added starlette dependency
2. `backend/Dockerfile` - Fixed dependency installation
3. `docker-compose.prod.yml` - Removed auth restrictions
4. `.env.prod` - Created environment file
5. `deploy-production.sh` - Created deployment script
6. `deploy-dev.sh` - Created development script
7. `backend/init_db.py` - Improved logging and error handling