# 404 Errors Fix Documentation

## Problem Analysis

The logs showed two main 404 errors:

1. **GET /metrics HTTP/1.1" 404** - Prometheus was trying to scrape metrics from a non-existent endpoint
2. **GET /api/api/v1/auth/me HTTP/1.0" 404** - Double `/api` prefix causing routing issues

## Root Causes

### 1. Missing Metrics Endpoint
- Prometheus configuration in `monitoring/prometheus.yml` was configured to scrape `/metrics` from FastAPI
- FastAPI application didn't have a `/metrics` endpoint
- This caused Prometheus monitoring to fail

### 2. Double `/api` Prefix Issue
- Nginx configuration had conflicting location blocks:
  - `/api/auth/` → proxied to NextJS frontend
  - `/api/` → proxied to FastAPI backend
- When requests came to `/api/api/v1/auth/me`, they matched the first block and were sent to NextJS
- NextJS doesn't have this endpoint, resulting in 404

## Solutions Applied

### 1. Added Metrics Endpoint to FastAPI

**File: `backend/main.py`**

```python
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram
import time
from fastapi.responses import Response

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')

# Middleware for metrics
@app.middleware("http")
async def metrics_middleware(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_LATENCY.observe(duration)
    
    return response

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
```

**Benefits:**
- ✅ Prometheus can now scrape metrics
- ✅ Request count and latency monitoring
- ✅ Standard Prometheus format

### 2. Fixed Nginx Routing Configuration

**Files Updated:**
- `nginx/nginx.prod.conf`
- `nginx/nginx.prod.improved.conf`
- `nginx/default.conf`

**Before:**
```nginx
location /api/auth/ {
    proxy_pass http://nextjs_frontend;  # All auth routes to NextJS
}

location /api/ {
    proxy_pass http://fastapi_backend;  # All other API routes to FastAPI
}
```

**After:**
```nginx
location /api/auth/ {
    # Only proxy NextAuth.js specific routes to frontend
    if ($request_uri ~ "^/api/auth/(callback|signin|signout|session|csrf|providers)") {
        proxy_pass http://nextjs_frontend;
        # ... NextJS specific settings
        break;
    }
    
    # All other auth routes go to FastAPI
    proxy_pass http://fastapi_backend;
    # ... FastAPI settings
}
```

**Benefits:**
- ✅ NextAuth.js routes still work correctly
- ✅ FastAPI auth endpoints (`/api/v1/auth/me`) work correctly
- ✅ No more double `/api` prefix issues
- ✅ Proper separation of concerns

## Testing the Fixes

### Run the Fix Script
```bash
./fix-404-errors.sh
```

### Test the Fixes
```bash
./test-404-fixes.sh
```

### Manual Testing

1. **Test Metrics Endpoint:**
   ```bash
   curl http://localhost:8000/metrics
   ```

2. **Test Auth Endpoint:**
   ```bash
   curl http://localhost:8000/api/v1/auth/me
   # Should return 401 (authentication required)
   ```

3. **Test Through Nginx:**
   ```bash
   curl http://localhost/api/v1/auth/me
   # Should return 401 (authentication required)
   ```

4. **Test Double API Prefix:**
   ```bash
   curl http://localhost/api/api/v1/auth/me
   # Should return 404 (as expected)
   ```

## Expected Results

After applying the fixes:

- ✅ `/metrics` endpoint returns Prometheus metrics
- ✅ `/api/v1/auth/me` returns 401 (authentication required, not 404)
- ✅ `/api/api/v1/auth/me` returns 404 (correct behavior)
- ✅ Prometheus can successfully scrape metrics
- ✅ No more 404 errors in logs for these endpoints

## Monitoring

The metrics endpoint now provides:
- `http_requests_total` - Total request count by method, endpoint, and status
- `http_request_duration_seconds` - Request latency histogram

These metrics can be viewed in Prometheus and Grafana dashboards.

## Files Modified

1. `backend/main.py` - Added metrics endpoint and middleware
2. `nginx/nginx.prod.conf` - Fixed auth routing
3. `nginx/nginx.prod.improved.conf` - Fixed auth routing
4. `nginx/default.conf` - Fixed auth routing
5. `fix-404-errors.sh` - Automation script
6. `test-404-fixes.sh` - Testing script
7. `404_ERRORS_FIX.md` - This documentation

## Dependencies

The `prometheus-client` package was already included in `backend/requirements.txt`, so no additional dependencies were needed.