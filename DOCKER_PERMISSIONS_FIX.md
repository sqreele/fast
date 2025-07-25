# Docker Permission Issues Fix

## Problem
The Next.js frontend container is encountering permission errors when trying to write to:
- `/app/next-env.d.ts`
- `/app/.next/trace`

This is a common issue when running Docker containers with volume mounts where the container user doesn't have write permissions to the mounted directories.

## Solution

### 1. Fix Permissions First
Run the permission fix script:
```bash
chmod +x fix-permissions.sh
./fix-permissions.sh
```

### 2. Restart Docker Development Environment
Use the restart script to rebuild and start containers:
```bash
chmod +x restart-dev.sh
./restart-dev.sh
```

### Alternative Manual Steps

If the scripts don't work, you can manually:

1. **Stop existing containers:**
   ```bash
   docker-compose down
   # or
   docker compose down
   ```

2. **Fix permissions:**
   ```bash
   sudo chown -R $(id -u):$(id -g) .
   chmod -R 777 frontend/
   mkdir -p frontend/.next
   touch frontend/next-env.d.ts
   ```

3. **Rebuild and start:**
   ```bash
   docker-compose up --build
   # or
   docker compose up --build
   ```

## Changes Made

1. **Updated `frontend/Dockerfile.dev`:**
   - Removed user creation that was causing conflicts
   - Set directory permissions to 777 for maximum compatibility
   - Simplified the container setup

2. **Updated `docker-compose.override.yml`:**
   - Removed user specification that was causing UID/GID mismatches

3. **Enhanced `fix-permissions.sh`:**
   - Added current user UID/GID detection
   - Set more permissive permissions (777) for Docker volume compatibility
   - Added ownership changes

## Expected Result

After applying these fixes, the Next.js development server should start successfully without permission errors:

```
✓ Starting...
✓ Ready in 2.1s
- Local:        http://localhost:3000
- Network:      http://172.18.0.5:3000
```

## Troubleshooting

If you still encounter issues:

1. **Check Docker is running:**
   ```bash
   docker ps
   ```

2. **Verify file permissions:**
   ```bash
   ls -la frontend/
   ```

3. **Check user ID matches:**
   ```bash
   id
   ```

4. **View container logs:**
   ```bash
   docker-compose logs frontend
   ```