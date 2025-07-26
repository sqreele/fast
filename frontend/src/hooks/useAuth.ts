import { useSession, signOut, getSession } from 'next-auth/react';
import { useCallback } from 'react';
import { authApi } from '../services/api';

export const useAuth = () => {
  const { data: session, status } = useSession();

  const logout = useCallback(async () => {
    console.log('Starting logout process...');
    
    try {
      // First, try to logout from backend to blacklist the token
      const currentSession = await getSession();
      if (currentSession?.accessToken) {
        try {
          await authApi.logout();
          console.log('Backend logout successful');
        } catch (backendError) {
          console.warn('Backend logout failed, continuing with frontend logout:', backendError);
          // Continue with frontend logout even if backend fails
        }
      }
      
      // Then clear the NextAuth session
      await signOut({ 
        callbackUrl: '/',
        redirect: true 
      });
      
      console.log('Logout completed successfully');
    } catch (error) {
      console.error('Logout error:', error);
      // Force redirect to home page even if there's an error
      window.location.href = '/';
    }
  }, []);

  const isAuthenticated = status === 'authenticated';
  const isLoading = status === 'loading';

  return {
    session,
    user: session?.user,
    isAuthenticated,
    isLoading,
    logout
  };
};