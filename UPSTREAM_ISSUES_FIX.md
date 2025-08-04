# Nginx Upstream Issues Fix Guide

## Problem Analysis

Based on the nginx logs you provided, your production environment is experiencing several upstream connection issues:

### Error Types Identified:

1. **Connection Refused (111)**: `connect() failed (111: Connection refused) while connecting to upstream`
   - **Cause**: Upstream servers are not running or not listening on the expected ports
   - **Affected Services**: `172.18.0.9:3000`, `172.18.0.10:3000` (Frontend containers)

2. **No Live Upstreams**: `no live upstreams while connecting to upstream`
   - **Cause**: All servers in the upstream group are down or unreachable
   - **Affected Services**: `nextjs_frontend` upstream group

3. **Connection Timeouts**: `upstream timed out (110: Operation timed out)`
   - **Cause**: Services are starting slowly or have resource constraints
   - **Affected Services**: Admin routes (`/admin`)

4. **Upstream Server Temporarily Disabled**: `upstream server temporarily disabled while connecting to upstream`
   - **Cause**: Nginx has marked servers as failed due to repeated connection failures

## Root Causes

1. **Frontend containers are not running** - The Next.js frontend services are down
2. **Backend containers may be down** - FastAPI services are not responding
3. **Network connectivity issues** between nginx and application containers
4. **Resource constraints** causing slow startup times
5. **Configuration issues** in nginx upstream settings

## Solutions

### Quick Fix (Recommended First Step)

Run the quick fix script to restart services and test connectivity:

```bash
./quick-upstream-fix.sh
```

### Diagnostic Analysis

If the quick fix doesn't resolve the issue, run the diagnostic script to identify specific problems:

```bash
./diagnose-upstream-issues.sh
```

### Comprehensive Fix

For a complete solution that rebuilds and reconfigures everything:

```bash
./fix-production-upstream-issues.sh
```

## Manual Fix Steps

If you prefer to fix issues manually, follow these steps:

### Step 1: Check Container Status

```bash
# Check running containers
docker ps

# Check all containers (including stopped)
docker ps -a

# Check Docker Compose status
docker compose -f docker-compose.prod.yml ps
```

### Step 2: Restart Services

```bash
# Stop all services
docker compose -f docker-compose.prod.yml down

# Start services with environment file
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d

# Wait for services to initialize
sleep 45
```

### Step 3: Verify Service Health

```bash
# Check if all services are running
docker compose -f docker-compose.prod.yml ps

# Test nginx configuration
docker compose -f docker-compose.prod.yml exec nginx nginx -t

# Reload nginx if needed
docker compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

### Step 4: Test Connectivity

```bash
# Test internal connectivity from nginx
docker compose -f docker-compose.prod.yml exec nginx curl -f http://fastapi:8000/health
docker compose -f docker-compose.prod.yml exec nginx curl -f http://frontend:3000/

# Test external connectivity
curl -I http://localhost/health
curl -I http://localhost/
curl -I http://localhost/api/health
```

## Configuration Improvements

The fix scripts include several improvements to prevent future issues:

### 1. Increased Timeouts

```nginx
# Increased proxy timeouts for better reliability
proxy_connect_timeout 120s;
proxy_send_timeout 120s;
proxy_read_timeout 120s;
```

### 2. Better Upstream Configuration

```nginx
# Improved upstream with better fail handling
upstream nextjs_frontend {
    least_conn;
    server frontend:3000 max_fails=5 fail_timeout=60s;
    keepalive 32;
}
```

### 3. Enhanced Error Handling

```nginx
# Better error pages and fallbacks
error_page 404 /404.html;
error_page 500 502 503 504 /50x.html;
```

## Monitoring and Prevention

### 1. Health Checks

Add health check endpoints to your services:

```yaml
# In docker-compose.prod.yml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:3000/"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### 2. Log Monitoring

Monitor logs for early detection:

```bash
# Watch nginx logs
docker compose -f docker-compose.prod.yml logs -f nginx

# Watch all service logs
docker compose -f docker-compose.prod.yml logs -f
```

### 3. Resource Monitoring

Check resource usage:

```bash
# Check container resource usage
docker stats

# Check system resources
df -h
free -h
```

## Common Issues and Solutions

### Issue: "No live upstreams"

**Symptoms**: All requests return 502 errors
**Solution**: 
1. Check if frontend containers are running
2. Restart frontend services
3. Verify network connectivity

### Issue: "Connection refused"

**Symptoms**: Specific upstream servers fail
**Solution**:
1. Check if the specific container is running
2. Verify the container is listening on the correct port
3. Check container logs for startup errors

### Issue: "Connection timeout"

**Symptoms**: Requests take too long and eventually fail
**Solution**:
1. Increase timeout values in nginx configuration
2. Check for resource constraints
3. Optimize application startup time

### Issue: "Upstream server temporarily disabled"

**Symptoms**: Intermittent failures with some requests working
**Solution**:
1. Adjust `max_fails` and `fail_timeout` values
2. Check for intermittent network issues
3. Monitor container health

## Environment Variables

Ensure your `.env.prod` file contains all necessary variables:

```bash
# Database Configuration
POSTGRES_PASSWORD=your_secure_password
POSTGRES_USER=pm_user
POSTGRES_DB=pm_database

# Redis Configuration
REDIS_PASSWORD=your_redis_password

# NextAuth Configuration
NEXTAUTH_URL=http://your-domain.com
NEXTAUTH_SECRET=your_nextauth_secret
NEXT_PUBLIC_BACKEND_URL=http://your-domain.com/api

# FastAPI Configuration
SECRET_KEY=your_fastapi_secret

# Grafana Configuration
GRAFANA_ADMIN_PASSWORD=your_grafana_password
```

## Troubleshooting Commands

### Check Service Status
```bash
docker compose -f docker-compose.prod.yml ps
```

### View Service Logs
```bash
# All services
docker compose -f docker-compose.prod.yml logs

# Specific service
docker compose -f docker-compose.prod.yml logs nginx
docker compose -f docker-compose.prod.yml logs frontend
docker compose -f docker-compose.prod.yml logs fastapi
```

### Restart Specific Service
```bash
docker compose -f docker-compose.prod.yml restart nginx
docker compose -f docker-compose.prod.yml restart frontend
docker compose -f docker-compose.prod.yml restart fastapi
```

### Rebuild and Restart
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

### Check Network Connectivity
```bash
# From nginx container
docker compose -f docker-compose.prod.yml exec nginx ping fastapi
docker compose -f docker-compose.prod.yml exec nginx ping frontend

# Test HTTP connectivity
docker compose -f docker-compose.prod.yml exec nginx curl -v http://fastapi:8000/health
docker compose -f docker-compose.prod.yml exec nginx curl -v http://frontend:3000/
```

## Prevention Best Practices

1. **Use Health Checks**: Implement proper health checks for all services
2. **Monitor Resources**: Keep an eye on CPU, memory, and disk usage
3. **Regular Updates**: Keep Docker images and dependencies updated
4. **Backup Configuration**: Always backup configuration files before changes
5. **Test Changes**: Test configuration changes in a staging environment first
6. **Log Rotation**: Implement proper log rotation to prevent disk space issues
7. **Resource Limits**: Set appropriate resource limits for containers

## Emergency Recovery

If all else fails, use the emergency recovery procedure:

```bash
# Stop everything
docker compose -f docker-compose.prod.yml down --volumes

# Clean up
docker system prune -f

# Rebuild from scratch
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build
```

## Support

If you continue to experience issues after following this guide:

1. Run the diagnostic script: `./diagnose-upstream-issues.sh`
2. Collect logs: `docker compose -f docker-compose.prod.yml logs > logs.txt`
3. Check system resources: `df -h && free -h && docker system df`
4. Review the troubleshooting output for specific error messages

The scripts provided will help automate most of these processes and provide detailed feedback on what's working and what needs attention.