# Authentication Setup with NextAuth.js

This document describes the authentication system setup for the PM System using NextAuth.js.

## Components

### 1. NextAuth.js Configuration
- **Location**: `frontend/src/app/api/auth/[...nextauth]/route.ts`
- **Provider**: Credentials provider for username/password authentication
- **Backend Integration**: Communicates with FastAPI backend for user verification

### 2. Nginx Configuration
- **Location**: `nginx/default.conf`
- **Purpose**: Routes authentication requests properly between frontend and backend
- **Key Routes**:
  - `/api/auth/*` → NextAuth.js (frontend)
  - `/api/*` → FastAPI backend
  - All other routes → Next.js frontend

### 3. Environment Variables

#### Required for Development (.env.local):
```env
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-nextauth-secret-key-change-in-production
BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_BACKEND_URL=http://localhost/api/v1
NODE_ENV=development
```

#### Required for Production:
```env
NEXTAUTH_URL=https://yourdomain.com
NEXTAUTH_SECRET=very-secure-secret-key-minimum-32-characters
BACKEND_URL=http://fastapi:8000
NEXT_PUBLIC_BACKEND_URL=https://yourdomain.com/api/v1
NODE_ENV=production
```

## Authentication Flow

1. User clicks "Login" on the dashboard
2. User is redirected to `/api/auth/siginin`
3. User enters credentials
4. NextAuth.js sends POST request to backend `/api/v1/auth/login`
5. Backend validates credentials and returns user data with token
6. NextAuth.js creates session with JWT strategy
7. User is redirected back to dashboard

## Pages

- **Sign In**: `/api/auth/siginin/page.tsx`
- **Sign Out**: `/api/auth/signout/page.tsx`
- **Error**: `/api/auth/error/page.tsx`

## Troubleshooting

### Common Issues:

1. **401 Unauthorized errors**
   - Check BACKEND_URL environment variable
   - Verify backend is running and accessible
   - Check nginx routing configuration

2. **NEXTAUTH_SECRET warnings**
   - Set NEXTAUTH_SECRET environment variable
   - Use minimum 32 characters for production

3. **Redirect loops**
   - Verify NEXTAUTH_URL matches your domain
   - Check nginx proxy headers configuration

4. **Backend connection errors**
   - For Docker: Use `http://fastapi:8000` as BACKEND_URL
   - For local development: Use `http://localhost:8000`

### Debug Mode

Enable NextAuth.js debug mode by setting:
```env
NEXTAUTH_DEBUG=true
```

### Logs

Check Docker logs for debugging:
```bash
docker-compose logs frontend
docker-compose logs nginx
docker-compose logs fastapi
```

## Security Considerations

1. Always use HTTPS in production
2. Set strong NEXTAUTH_SECRET (32+ characters)
3. Keep environment variables secure
4. Regularly rotate secrets
5. Configure proper CORS settings

## Testing Authentication

1. Start the application:
   ```bash
   docker-compose up -d
   ```

2. Navigate to `http://localhost`
3. Click "Login" button
4. Enter valid credentials (configure in backend)
5. Verify successful authentication

## Backend Requirements

The backend must provide:
- `POST /api/v1/auth/login` endpoint
- Accept JSON with `username` and `password`
- Return user object with `token` field on success
- Return appropriate HTTP status codes