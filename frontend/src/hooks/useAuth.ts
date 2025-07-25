import { useSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export function useAuth(requireAuth: boolean = false) {
  const { data: session, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (requireAuth && status === 'unauthenticated') {
      router.push('/api/auth/signin');
    }
  }, [requireAuth, status, router]);

  return {
    session,
    status,
    isLoading: status === 'loading',
    isAuthenticated: status === 'authenticated',
    user: session?.user,
    role: session?.user?.role,
    accessToken: session?.accessToken
  };
}

export function useRequireAuth() {
  return useAuth(true);
}

export function useRole() {
  const { role, isAuthenticated } = useAuth();
  
  const hasRole = (requiredRole: string) => {
    return isAuthenticated && role === requiredRole;
  };
  
  const hasAnyRole = (requiredRoles: string[]) => {
    return isAuthenticated && role && requiredRoles.includes(role);
  };
  
  const isAdmin = () => hasRole('ADMIN');
  const isManager = () => hasRole('MANAGER');
  const isTechnician = () => hasRole('TECHNICIAN');
  
  return {
    role,
    hasRole,
    hasAnyRole,
    isAdmin,
    isManager,
    isTechnician
  };
}