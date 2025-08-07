# Login Redirect Issue Fix

## Problem Description

After successful login in production, users were being redirected to `localhost` instead of the production domain (`http://206.189.89.239`). This caused authentication failures and poor user experience.

## Root Cause Analysis

The issue was caused by two main problems:

### 1. Incorrect Fallback URL in auth-utils.ts

**File**: `frontend/src/lib/auth-utils.ts`

**Problem**: The production fallback was hardcoded to `localhost`:

```typescript
// Fallbacks based on environment
if (process.env.NODE_ENV === 'production') {
  return 'http://localhost';  // ← WRONG!
}
```

**Impact**: When `NEXTAUTH_URL` environment variable wasn't properly resolved, the system defaulted to localhost.

### 2. Insufficient Redirect Validation in NextAuth

**File**: `frontend/src/lib/authOptions.ts`

**Problem**: The redirect callback didn't have proper validation for production environments and lacked debugging information.

## Solution Implemented

### 1. Fixed Production Fallback URL

**File**: `frontend/src/lib/auth-utils.ts`

**Fix**: Updated the production fallback to use the correct production IP:

```typescript
// Fallbacks based on environment
if (process.env.NODE_ENV === 'production') {
  // Use the production IP address instead of localhost
  return 'http://206.189.89.239';
}
```

### 2. Enhanced NextAuth Redirect Callback

**File**: `frontend/src/lib/authOptions.ts`

**Improvements**:
- Added comprehensive logging for debugging redirect issues
- Added production environment detection
- Enhanced URL validation
- Prevented localhost redirects in production

```typescript
async redirect({ url, baseUrl }) {
  // Add logging for debugging redirect issues
  console.log('NextAuth redirect called:', { url, baseUrl });
  
  // Always redirect to baseUrl to avoid invalid URLs
  if (url.startsWith('/')) {
    const redirectUrl = `${baseUrl}${url}`;
    console.log('Redirecting to:', redirectUrl);
    return redirectUrl;
  }
  
  // Check if URL is from the same origin
  try {
    if (new URL(url).origin === baseUrl) {
      console.log('Redirecting to same origin URL:', url);
      return url;
    }
  } catch (error) {
    console.warn('Invalid URL in redirect:', url, error);
  }
  
  // Ensure we don't redirect to localhost in production
  if (process.env.NODE_ENV === 'production' && baseUrl.includes('localhost')) {
    const productionUrl = process.env.NEXTAUTH_URL || 'http://206.189.89.239';
    console.log('Production environment detected, redirecting to:', productionUrl);
    return productionUrl;
  }
  
  console.log('Final redirect to baseUrl:', baseUrl);
  return baseUrl;
},
```

## Environment Configuration

### Current Production Configuration

**File**: `.env.prod`

```bash
NEXTAUTH_URL=http://206.189.89.239
NEXTAUTH_SECRET=b9dc9437cd27ef4566cef5e97713b4de95e2f56bcb770ad272fc68d725bdb17b
BACKEND_URL=http://fastapi:8000
NEXT_PUBLIC_BACKEND_URL=http://206.189.89.239/api/v1
```

### Verification Steps

1. **Check NEXTAUTH_URL**: Ensure it matches your production domain
2. **Verify Environment**: Confirm `NODE_ENV=production` is set
3. **Test Redirects**: Monitor browser console for redirect logs

## Deployment

### Automatic Fix Script

Use the provided script to automatically deploy the fix:

```bash
./fix-login-redirect.sh
```

### Manual Deployment Steps

1. **Stop containers**:
   ```bash
   docker-compose -f docker-compose.prod.yml --env-file .env.prod down
   ```

2. **Rebuild frontend**:
   ```bash
   docker-compose -f docker-compose.prod.yml --env-file .env.prod build frontend
   ```

3. **Start containers**:
   ```bash
   docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
   ```

## Testing the Fix

### 1. Login Flow Test

1. Visit: `http://206.189.89.239/signin`
2. Enter valid credentials
3. Verify redirect goes to `http://206.189.89.239` (not localhost)

### 2. Browser Console Monitoring

Check browser console for redirect logs:
```
NextAuth redirect called: { url: "/", baseUrl: "http://206.189.89.239" }
Redirecting to: http://206.189.89.239/
```

### 3. Network Tab Verification

In browser DevTools Network tab:
- Verify redirects go to production domain
- Check for any localhost requests
- Confirm authentication cookies are set correctly

## Prevention Measures

### 1. Environment Validation

Add environment validation to prevent similar issues:

```typescript
// Validate production environment
if (process.env.NODE_ENV === 'production') {
  if (!process.env.NEXTAUTH_URL || process.env.NEXTAUTH_URL.includes('localhost')) {
    throw new Error('Invalid NEXTAUTH_URL for production environment');
  }
}
```

### 2. Automated Testing

Add integration tests for authentication flow:

```typescript
// Test redirect after login
test('should redirect to production domain after login', async () => {
  // Test implementation
});
```

### 3. Monitoring and Alerting

- Monitor for localhost redirects in production
- Set up alerts for authentication failures
- Log redirect patterns for analysis

## Troubleshooting

### Common Issues

1. **Still redirecting to localhost**:
   - Check if containers were rebuilt with new code
   - Verify `.env.prod` has correct `NEXTAUTH_URL`
   - Clear browser cache and cookies

2. **Authentication errors**:
   - Check browser console for redirect logs
   - Verify backend is accessible from frontend container
   - Confirm environment variables are loaded correctly

3. **Environment variable issues**:
   - Ensure `.env.prod` is being used by docker-compose
   - Check for typos in environment variable names
   - Verify no conflicting environment files

### Debug Commands

```bash
# Check container environment
docker-compose -f docker-compose.prod.yml --env-file .env.prod exec frontend env | grep NEXTAUTH

# View container logs
docker-compose -f docker-compose.prod.yml --env-file .env.prod logs frontend

# Test frontend health
curl -f http://206.189.89.239/health
```

## Files Modified

1. `frontend/src/lib/auth-utils.ts` - Fixed production fallback URL
2. `frontend/src/lib/authOptions.ts` - Enhanced redirect callback
3. `fix-login-redirect.sh` - Deployment script
4. `LOGIN_REDIRECT_FIX.md` - This documentation

## Related Documentation

- `AUTHENTICATION_SETUP.md` - General authentication setup
- `PRODUCTION_ISSUES_FIXED.md` - Other production fixes
- `NEXTAUTH_CLIENT_FETCH_ERROR_FIX.md` - NextAuth error fixes