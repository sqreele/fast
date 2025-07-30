# Docker Compose Scaling Setup

## Problem Solved
The original error was caused by trying to scale the frontend service while having a fixed port mapping (`3000:3000`). When scaling to 2 instances, both containers tried to bind to the same host port 3000, causing a conflict.

## Changes Made

### 1. Removed Fixed Container Names
- Removed `container_name` from `fastapi` and `frontend` services
- This allows Docker Compose to create multiple instances with auto-generated names

### 2. Changed Port Mapping to Expose
- Changed `ports: - "3000:3000"` to `expose: - "3000"` for frontend
- Changed `ports: - "8000:8000"` to `expose: - "8000"` for fastapi
- Services are now only accessible internally through nginx

### 3. Load Balancing Through Nginx
- Nginx is configured to load balance between all instances
- All external traffic goes through nginx on port 80
- Frontend: `http://localhost`
- API: `http://localhost/api/v1`

## Usage

### Standard (Single Instance)
```bash
docker compose up -d
```

### Scaled (Multiple Instances)
```bash
# Using the provided script
./run-scaled.sh

# Or manually
docker compose up -d --scale frontend=2 --scale fastapi=2
```

### Check Status
```bash
docker compose ps
```

### View Logs
```bash
docker compose logs -f
```

### Stop Services
```bash
docker compose down
```

## Benefits
- **High Availability**: Multiple instances provide redundancy
- **Load Distribution**: Requests are distributed across instances
- **Zero Downtime**: Can scale up/down without port conflicts
- **Simple Access**: Single entry point through nginx (port 80)

## Development Mode
For development, the override file (`docker-compose.override.yml`) still works normally with hot reload and development settings.