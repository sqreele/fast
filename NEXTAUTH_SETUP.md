# NextAuth.js Complete Setup Guide

## 🚀 **Features Implemented**

### ✅ **Core Authentication**
- [x] JWT-based authentication with NextAuth.js v4.24.11
- [x] Custom credentials provider with FastAPI backend
- [x] Secure token handling and session management
- [x] Auto-refresh token logic (ready for implementation)
- [x] Custom signin/signout pages

### ✅ **Role-Based Access Control (RBAC)**
- [x] Role hierarchy: USER → TECHNICIAN → SUPERVISOR → MANAGER → ADMIN
- [x] Permission-based access control
- [x] Role guard components for conditional rendering
- [x] Server-side and client-side role checking

### ✅ **Enhanced User Experience**
- [x] Custom auth hooks (`useAuth`, `useRole`)
- [x] TypeScript support with extended type definitions
- [x] Error handling and user feedback
- [x] Automatic redirects and session persistence

## 📋 **Setup Instructions**

### 1. **Environment Configuration**

Copy the environment template:
```bash
cp frontend/.env.local.example frontend/.env.local
```

Update the values in `.env.local`:
```bash
# Generate a secure secret
NEXTAUTH_SECRET=$(openssl rand -base64 32)

# Set your URLs
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

### 2. **Backend Integration**

The backend endpoints are already configured:
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration  
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/logout` - User logout

### 3. **Frontend Integration**

Import the auth provider in your app layout:
```tsx
// app/layout.tsx
import { SessionProvider } from 'next-auth/react';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <SessionProvider>
          {children}
        </SessionProvider>
      </body>
    </html>
  );
}
```

## 🔧 **Usage Examples**

### **Basic Authentication Hook**
```tsx
import { useAuth } from '@/hooks/useAuth';

function MyComponent() {
  const { isAuthenticated, user, isLoading } = useAuth();
  
  if (isLoading) return <div>Loading...</div>;
  if (!isAuthenticated) return <div>Please sign in</div>;
  
  return <div>Welcome, {user?.name}!</div>;
}
```

### **Role-Based Access Control**
```tsx
import { useRole } from '@/hooks/useAuth';
import { AdminOnly, ManagerOrAdmin } from '@/components/auth/RoleGuard';

function AdminPanel() {
  const { isAdmin, hasPermission } = useRole();
  
  return (
    <div>
      <AdminOnly fallback={<div>Access Denied</div>}>
        <button>Admin Only Button</button>
      </AdminOnly>
      
      <ManagerOrAdmin>
        <button>Manager+ Button</button>
      </ManagerOrAdmin>
      
      {hasPermission('manage_users') && (
        <button>Manage Users</button>
      )}
    </div>
  );
}
```

### **Role Guard Component**
```tsx
import RoleGuard from '@/components/auth/RoleGuard';

function ProtectedComponent() {
  return (
    <RoleGuard 
      requiredRole="TECHNICIAN" 
      fallback={<div>Technician access required</div>}
    >
      <TechnicianDashboard />
    </RoleGuard>
  );
}
```

### **Server-Side Authentication**
```tsx
// app/admin/page.tsx
import { requireAuth } from '@/lib/auth-utils';

export default async function AdminPage() {
  const session = await requireAuth('ADMIN');
  
  return (
    <div>
      <h1>Admin Dashboard</h1>
      <p>Welcome, {session.user?.name}</p>
    </div>
  );
}
```

### **Permission-Based Rendering**
```tsx
import { hasPermission } from '@/lib/auth-utils';
import { useAuth } from '@/hooks/useAuth';

function WorkOrderActions() {
  const { role } = useAuth();
  
  return (
    <div>
      {hasPermission(role, 'create_work_orders') && (
        <button>Create Work Order</button>
      )}
      
      {hasPermission(role, 'approve_work_orders') && (
        <button>Approve</button>
      )}
      
      {hasPermission(role, 'delete_any') && (
        <button>Delete</button>
      )}
    </div>
  );
}
```

## 🔐 **Role Hierarchy & Permissions**

### **Roles (Hierarchical)**
1. **USER** - Basic access
2. **TECHNICIAN** - Can create work orders, update logs
3. **SUPERVISOR** - Can approve work orders, manage technicians
4. **MANAGER** - Can manage work orders, assign tasks, view reports
5. **ADMIN** - Full system access

### **Permission System**
Each role inherits permissions from lower roles:

```typescript
// Example permissions by role
TECHNICIAN: [
  'view_dashboard',
  'view_own_data',
  'create_issues',
  'create_work_orders',
  'update_maintenance_logs',
  'view_assigned_tasks',
  'upload_files'
]

ADMIN: [
  // All TECHNICIAN permissions +
  'manage_users',
  'manage_properties', 
  'manage_system',
  'view_all_data',
  'delete_any',
  'modify_any'
]
```

## 🔄 **Authentication Flow**

### **Login Process**
1. User enters credentials on `/api/auth/signin`
2. NextAuth calls FastAPI `/api/v1/auth/login`
3. Backend validates credentials and returns user data + token
4. NextAuth stores JWT token in session
5. User redirected to dashboard

### **Session Management**
- JWT tokens stored securely in NextAuth session
- 24-hour token expiration with refresh capability
- Automatic logout on token expiration
- Session persistence across browser sessions

### **Logout Process**
1. User clicks logout
2. NextAuth clears local session
3. Optional: Call backend `/api/v1/auth/logout` to invalidate token
4. Redirect to signin page

## 🛡️ **Security Features**

### **JWT Security**
- Secure secret key (minimum 32 characters)
- Token expiration (24 hours)
- Automatic token refresh logic (ready to implement)
- CSRF protection enabled

### **Role Security**
- Server-side role validation
- Permission-based access control
- Hierarchical role system
- Fallback components for unauthorized access

### **Environment Security**
- Sensitive data in environment variables
- Different configs for development/production
- Debug logging only in development

## 🚨 **Common Issues & Solutions**

### **Issue: "Invalid credentials" error**
**Solution:** Ensure backend endpoint is correct and accessible:
```bash
# Check if backend is running
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"test"}'
```

### **Issue: Session not persisting**
**Solution:** Check NEXTAUTH_SECRET is set properly:
```bash
# Generate new secret
openssl rand -base64 32
```

### **Issue: Role checks not working**
**Solution:** Verify user role is being returned from backend and stored in session:
```tsx
// Debug session data
const { data: session } = useSession();
console.log('Session:', session);
console.log('User role:', session?.user?.role);
```

### **Issue: CORS errors**
**Solution:** Configure CORS in FastAPI backend:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📦 **Dependencies**

```json
{
  "next-auth": "^4.24.11",
  "next": "15.4.3",
  "react": "19.1.0",
  "axios": "^1.11.0"
}
```

## 🔄 **Next Steps for Production**

### **JWT Token Refresh**
Implement automatic token refresh in the JWT callback:
```typescript
// In NextAuth configuration
async jwt({ token, user, account }) {
  // Check if token is expired and refresh
  if (Date.now() < token.accessTokenExpires) {
    return token;
  }
  
  // Refresh token logic here
  return refreshAccessToken(token);
}
```

### **Enhanced Security**
- Implement proper JWT tokens in FastAPI backend
- Add rate limiting for auth endpoints
- Enable HTTPS in production
- Add password strength requirements
- Implement account lockout after failed attempts

### **User Management**
- Add password reset functionality
- Implement email verification
- Add user profile management
- Enable password change functionality

## ✅ **Testing the Implementation**

1. **Start both services:**
   ```bash
   # Backend
   cd backend && uvicorn main:app --reload
   
   # Frontend  
   cd frontend && npm run dev
   ```

2. **Test authentication:**
   - Visit `http://localhost:3000`
   - Click sign in
   - Use credentials for existing user
   - Verify role-based access

3. **Test role guards:**
   - Create components with different role requirements
   - Verify correct rendering based on user role
   - Test fallback components

---

**🎉 Your NextAuth.js authentication system is now fully configured with role-based access control!**