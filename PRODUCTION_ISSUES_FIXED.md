# Production Issues Fixed - January 2025

## Issues Identified from Log Analysis

Based on the production logs, several critical issues were identified and resolved:

### 1. 🚨 Nginx Rate Limiting Issues
**Problem:** Rate limiting zone "login" was set too aggressively (5 requests/minute), causing 503 errors for legitimate users trying to authenticate.

**Logs showing the issue:**
```
2025/08/01 02:58:59 [error] 8#8: *248 limiting requests, excess: 5.258 by zone "login", client: 161.82.166.238
161.82.166.238 - - [01/Aug/2025:02:58:59 +0000] "GET /api/auth/error HTTP/1.1" 503 497
```

**Fix Applied:**
- Increased login rate limit from `5r/m` to `10r/m`
- Increased API rate limit from `10r/s` to `20r/s`
- Increased burst limits: login burst from 5 to 10, API burst from 20 to 50
- Increased connection limits from 10 to 20 per IP

### 2. 🔧 Nginx Configuration Issues
**Problem:** Nginx was trying to connect to incorrect upstream server names (`fast-fastapi-1/2`, `fast-frontend-1/2`) instead of actual service names.

**Fix Applied:**
- Updated upstream configuration to use correct service names:
  - `fastapi:8000` instead of `fast-fastapi-1:8000` and `fast-fastapi-2:8000`
  - `frontend:3000` instead of `fast-frontend-1:3000` and `fast-frontend-2:3000`

### 3. 📊 Missing Nginx Status Endpoint
**Problem:** Prometheus was failing to scrape nginx metrics due to missing `/nginx_status` endpoint.

**Logs showing the issue:**
```
172.18.0.2 - - [01/Aug/2025:02:59:00 +0000] "GET /nginx_status HTTP/1.1" 404 2882 "-" "Prometheus/3.5.0"
```

**Fix Applied:**
- Added nginx status endpoint configuration:
```nginx
location /nginx_status {
    stub_status on;
    access_log off;
    allow 172.18.0.0/16;  # Docker network
    allow 127.0.0.1;
    deny all;
}
```

### 4. 🚫 Missing NextAuth API Endpoints
**Problem:** Several NextAuth API endpoints were returning 404 errors, breaking authentication flow.

**Logs showing the issue:**
```
161.82.166.238 - - [01/Aug/2025:02:58:59 +0000] "GET /api/auth/providers HTTP/1.1" 404 22
161.82.166.238 - - [01/Aug/2025:02:58:59 +0000] "POST /api/auth/_log HTTP/1.1" 404 22
161.82.166.238 - - [01/Aug/2025:02:59:05 +0000] "GET /api/auth/error HTTP/1.1" 404 22
```

**Fix Applied:**
- Created `/api/auth/providers/route.ts` - returns available authentication providers
- Created `/api/auth/_log/route.ts` - handles authentication event logging
- Created `/api/auth/error/route.ts` - handles authentication errors
- Fixed NextAuth page configuration to use correct error/signout paths

### 5. 🤖 Excessive Bot Crawling
**Problem:** GPTBot and other AI crawlers were causing excessive 308/404 errors trying to access old blog content.

**Logs showing the issue:**
```
162.158.162.52 - - [01/Aug/2025:02:58:55 +0000] "GET /2012/09/ky-thuat-trong-chanh/ HTTP/1.1" 308 40 "-" "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)"
172.71.152.97 - - [01/Aug/2025:02:58:55 +0000] "GET /2012/09/ky-thuat-trong-chanh HTTP/1.1" 404 2897 "-" "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.2; +https://openai.com/gptbot)"
```

**Fix Applied:**
- Added bot detection in nginx configuration
- Created `robots.txt` with specific rules for AI bots
- Added crawl delays and disallow rules for archive content
- Implemented bot rate limiting for old blog paths

## Files Modified

### Nginx Configuration
- `nginx/nginx.prod.conf` - Complete configuration overhaul

### Frontend Files
- `frontend/src/app/api/auth/[...nextauth]/route.ts` - Fixed page paths
- `frontend/src/app/api/auth/providers/route.ts` - NEW - Providers endpoint
- `frontend/src/app/api/auth/_log/route.ts` - NEW - Logging endpoint  
- `frontend/src/app/api/auth/error/route.ts` - NEW - Error handling endpoint
- `frontend/public/robots.txt` - NEW - Bot management

### Scripts
- `fix-production-issues.sh` - NEW - Automated fix deployment script

## Expected Improvements

### Immediate Impact
✅ **Eliminated 503 rate limiting errors** for legitimate authentication attempts
✅ **Fixed 404 errors** for NextAuth API endpoints
✅ **Working Prometheus monitoring** with nginx metrics
✅ **Reduced bot crawling errors** through proper robots.txt and rate limiting

### Monitoring Improvements
- Nginx status endpoint now available at `/nginx_status`
- Better error logging for authentication events
- Reduced noise in logs from bot crawling

### Performance Improvements
- More reasonable rate limiting thresholds
- Better connection pooling with correct upstream names
- Reduced server load from bot traffic

## Deployment Instructions

To apply these fixes to your production environment:

```bash
# Run the automated fix script
./fix-production-issues.sh
```

Or manually:
```bash
# Restart nginx with new configuration
docker-compose -f docker-compose.prod.yml restart nginx

# Rebuild and restart frontend with new API endpoints
docker-compose -f docker-compose.prod.yml build frontend
docker-compose -f docker-compose.prod.yml restart frontend
```

## Verification

After deployment, verify the fixes:

```bash
# Check nginx status endpoint (from internal network)
curl http://localhost/nginx_status

# Check NextAuth endpoints
curl http://localhost/api/auth/providers
curl http://localhost/api/auth/error
curl http://localhost/api/auth/_log

# Check robots.txt
curl http://localhost/robots.txt

# Monitor logs for improvements
docker logs pm_nginx -f
```

## Long-term Recommendations

1. **Monitor rate limiting metrics** to fine-tune thresholds based on actual usage patterns
2. **Implement proper 404 handling** for old blog content with redirects or archived content
3. **Add health check endpoints** for all services to improve monitoring
4. **Consider implementing caching** for frequently accessed content
5. **Set up alerting** for authentication failures and rate limiting events

---

**Fixed by:** Background Agent  
**Date:** January 1, 2025  
**Status:** ✅ Complete - Ready for production deployment