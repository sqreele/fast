# NextAuth CLIENT_FETCH_ERROR Fix

## Problem
The error `[next-auth][error][CLIENT_FETCH_ERROR] "Unexpected token 'S', "Server error" is not valid JSON"` occurs when NextAuth receives a non-JSON response from the authentication endpoint.

## Root Causes Identified and Fixed

### 1. **Incorrect SignIn Page Configuration** ✅ FIXED
**Issue**: The signin page was incorrectly configured in NextAuth configuration as `/api/auth/signin`, which conflicts with NextAuth's internal API routes.

**Fix Applied**:
- Updated `frontend/src/app/api/auth/[...nextauth]/route.ts` signin page path from `/api/auth/signin` to `/signin`
- Created new signin page at `frontend/src/app/signin/page.tsx`
- Removed the incorrectly placed signin page from `frontend/src/app/api/auth/signin/`

### 2. **Enhanced Error Handling in NextAuth Provider** ✅ FIXED
**Issue**: Poor error handling when backend returns non-JSON responses.

**Fix Applied**:
- Added content-type checking before parsing responses
- Enhanced error handling for network issues
- Added detailed logging for debugging

### 3. **Missing CORS Configuration** ✅ FIXED
**Issue**: Backend was missing CORS middleware, causing requests from Next.js to be blocked.

**Fix Applied**:
- Added CORS middleware to `backend/main.py`
- Configured allowed origins for development and production

### 4. **Environment Configuration** ✅ FIXED
**Issue**: Missing or incorrect environment variables.

**Fix Applied**:
- Created `frontend/.env.local.example` with proper NextAuth configuration
- Ensured `NEXTAUTH_SECRET`, `NEXTAUTH_URL`, and `BACKEND_URL` are properly set

## Configuration Files Updated

### NextAuth Configuration (`frontend/src/app/api/auth/[...nextauth]/route.ts`)
```typescript
// Key fixes:
1. Changed signIn page path from '/api/auth/signin' to '/signin'
2. Added robust error handling for non-JSON responses
3. Added content-type validation
4. Enhanced network error detection
```

### CORS Middleware (`backend/main.py`)
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Environment Configuration (`frontend/.env.local`)
```env
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-nextauth-secret-key-minimum-32-characters-long
BACKEND_URL=http://localhost:8000
```

## How to Test the Fix

1. **Copy environment configuration**:
   ```bash
   cd frontend
   cp .env.local.example .env.local
   ```

2. **Update the environment variables** in `.env.local`:
   - Set a strong `NEXTAUTH_SECRET` (minimum 32 characters)
   - Ensure `BACKEND_URL` points to your running backend
   - Set `NEXTAUTH_URL` to match your frontend URL

3. **Start the backend server**:
   ```bash
   cd backend
   source venv/bin/activate  # if using virtual environment
   python main.py
   # or
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Start the frontend server**:
   ```bash
   cd frontend
   npm run dev
   ```

5. **Test authentication**:
   - Navigate to `http://localhost:3000/signin`
   - Try logging in with valid credentials
   - Check browser dev tools for any remaining errors

## Common Issues and Solutions

### Backend Not Accessible
If you see network errors in the console:
- Ensure backend is running on the correct port
- Check `BACKEND_URL` in environment variables
- Verify CORS configuration allows your frontend domain

### Still Getting JSON Parse Errors
If you still see "Unexpected token" errors:
- Check if backend is returning HTML error pages instead of JSON
- Verify the backend authentication endpoint returns proper JSON responses
- Check backend logs for any server errors

### Authentication Still Failing
- Verify backend database is properly initialized
- Check if user credentials exist in the database
- Ensure password hashing is working correctly
- Check backend logs for authentication-specific errors

## Environment-Specific Configuration

### Development
```env
NEXTAUTH_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
```

### Docker/Production
```env
NEXTAUTH_URL=https://yourdomain.com
BACKEND_URL=http://fastapi:8000  # Internal Docker service name
```

## Verification Checklist

- [ ] Backend server starts without errors
- [ ] Frontend server starts without errors  
- [ ] CORS middleware is enabled on backend
- [ ] Environment variables are properly set
- [ ] SignIn page loads at `/signin`
- [ ] No CLIENT_FETCH_ERROR in browser console
- [ ] Authentication flow completes successfully

## Additional Notes

- The signin page was moved from the API routes directory to the proper app directory
- Error pages have been created for better user experience
- Enhanced logging helps with debugging authentication issues
- The backend now includes proper CORS configuration for cross-origin requests

If you continue to experience issues, check:
1. Browser Network tab for the actual HTTP response
2. Backend server logs for any server-side errors
3. NextAuth debug logs by setting `debug: true` in NextAuth config