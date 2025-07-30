# Docker Build Troubleshooting Guide

## Error: "failed to execute bake: read |0: file already closed"

This error typically occurs when using Docker buildx with buildkit and indicates a build context or pipe closure issue.

### Quick Fixes (Try in Order)

#### 1. Use the Simple Build Script (Recommended)
```bash
# Use our custom build script that avoids buildx
./build-no-buildx.sh
```

#### 2. Use No-BuildX Docker Compose
```bash
# Build without buildx using our override file
make build-no-buildx

# Or directly:
DOCKER_BUILDKIT=0 COMPOSE_DOCKER_CLI_BUILD=0 docker-compose -f docker-compose.yml -f docker-compose.no-buildx.yml up --build
```

#### 3. Use Simple Dockerfile
```bash
# Build the FastAPI service with the simplified Dockerfile
docker build -f backend/Dockerfile.simple -t pm-fastapi:latest backend/
```

#### 4. Disable BuildKit Globally
```bash
# Disable buildkit for the current session
export DOCKER_BUILDKIT=0
export COMPOSE_DOCKER_CLI_BUILD=0

# Then run your normal build commands
docker-compose build
```

### Root Causes and Solutions

#### Cause 1: BuildX/BuildKit Issues
**Symptoms:** 
- "failed to execute bake" errors
- "read |0: file already closed"
- Build context transfer failures

**Solutions:**
- Use `DOCKER_BUILDKIT=0` to disable buildkit
- Use the simplified Dockerfile (`Dockerfile.simple`)
- Use regular `docker build` instead of `docker buildx`

#### Cause 2: Multi-Stage Build Problems
**Symptoms:**
- Builds fail at specific stages
- Intermittent failures
- Context copying issues

**Solutions:**
- Use single-stage builds (see `Dockerfile.simple`)
- Reduce build context size
- Add retry logic to pip installations

#### Cause 3: Network/Timeout Issues
**Symptoms:**
- Pip installation timeouts
- Package download failures
- Connection resets

**Solutions:**
- Add `--timeout=300` to pip commands
- Use `--retries=3` for pip installations
- Implement retry logic in build scripts

### Environment-Specific Solutions

#### For Development
```bash
# Quick development build
make build-simple

# Or use development-specific compose
docker-compose up --build
```

#### For Production
```bash
# Production build without buildx
DOCKER_BUILDKIT=0 docker-compose -f docker-compose.prod.yml build

# Or use the build script
./build-no-buildx.sh
```

#### For CI/CD Environments
```bash
# Set environment variables to disable buildx
export DOCKER_BUILDKIT=0
export COMPOSE_DOCKER_CLI_BUILD=0

# Use explicit build commands
docker build -t pm-fastapi:latest backend/
docker build -t pm-frontend:latest frontend/
docker build -t pm-nginx:latest nginx/
```

### Advanced Troubleshooting

#### 1. Clean Build Environment
```bash
# Remove all build cache
docker builder prune -af

# Remove all containers and images
docker system prune -af

# Remove buildx builders
docker buildx ls
docker buildx rm --all-inactive
```

#### 2. Check Docker Configuration
```bash
# Check Docker version and buildx status
docker version
docker buildx version
docker buildx ls

# Check available builders
docker buildx inspect
```

#### 3. Debug Build Process
```bash
# Enable debug logging
export BUILDX_EXPERIMENTAL=1
export DOCKER_CLI_EXPERIMENTAL=enabled

# Run build with verbose output
docker build --progress=plain -f backend/Dockerfile.simple backend/
```

### File Structure for Fixes

The following files have been created/modified to fix the buildx issues:

- `backend/Dockerfile.simple` - Single-stage Dockerfile without buildx dependencies
- `docker-compose.no-buildx.yml` - Override file that disables buildx
- `build-no-buildx.sh` - Build script with retry logic and error handling
- `Makefile` - Updated with no-buildx build targets

### Makefile Commands

```bash
# Standard build (may have buildx issues)
make build

# Build without buildx (recommended)
make build-no-buildx

# Build with custom script (most reliable)
make build-simple

# Development environment
make dev-build

# Production environment
make prod-build
```

### Prevention Tips

1. **Always test builds locally** before deploying
2. **Use the simplified Dockerfile** for production
3. **Set DOCKER_BUILDKIT=0** in CI/CD environments
4. **Monitor build logs** for early warning signs
5. **Keep Docker and docker-compose updated**

### When to Use Each Solution

| Scenario | Recommended Solution |
|----------|---------------------|
| Local development | `make build-simple` or `./build-no-buildx.sh` |
| Production deployment | `make build-no-buildx` |
| CI/CD pipeline | Set `DOCKER_BUILDKIT=0` + standard commands |
| Quick testing | `docker build -f backend/Dockerfile.simple` |
| Persistent issues | Use `Dockerfile.simple` exclusively |

### Getting Help

If you continue to experience issues:

1. Check the Docker daemon logs: `docker system events`
2. Verify available disk space: `df -h`
3. Check memory usage: `free -h`
4. Review the specific error messages in build logs
5. Try building individual services separately

Remember: The `build-no-buildx.sh` script is designed to handle most common build issues automatically with retry logic and fallback options.