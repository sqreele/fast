import { useSession, signOut, getSession } from 'next-auth/react';
import { useCallback } from 'react';
import { authApi } from '../services/api';

export const useAuth = () => {
  const { data: session, status } = useSession();

  const logout = useCallback(async () => {
    console.log('🔄 Starting logout process...');
    console.log('📊 Current session status:', status);
    console.log('👤 Current session data:', session ? 'exists' : 'null');
    
    try {
      // First, try to logout from backend to blacklist the token
      const currentSession = await getSession();
      console.log('🔍 Retrieved session for logout:', currentSession ? 'exists' : 'null');
      
      if (currentSession?.accessToken) {
        console.log('🎯 Access token found, attempting backend logout...');
        try {
          const backendResult = await authApi.logout();
          console.log('✅ Backend logout successful:', backendResult);
        } catch (backendError) {
          console.warn('❌ Backend logout failed, continuing with frontend logout:', backendError);
          // Log more details about the backend error
          if (backendError instanceof Error) {
            console.warn('Backend error details:', {
              message: backendError.message,
              name: backendError.name,
              stack: backendError.stack?.substring(0, 200)
            });
          }
        }
      } else {
        console.log('🔍 No access token found, skipping backend logout');
      }
      
      console.log('🚪 Attempting NextAuth signOut...');
      
      // Then clear the NextAuth session
      const signOutResult = await signOut({ 
        callbackUrl: '/',
        redirect: false  // Change this to false temporarily for debugging
      });
      
      console.log('✅ NextAuth signOut completed:', signOutResult);
      
      // Manual redirect after successful signOut
      console.log('🔄 Redirecting to home page...');
      window.location.href = '/';
      
    } catch (error) {
      console.error('❌ Logout error:', error);
      if (error instanceof Error) {
        console.error('Error details:', {
          message: error.message,
          name: error.name,
          stack: error.stack?.substring(0, 200)
        });
      }
      // Force redirect to home page even if there's an error
      console.log('🔄 Force redirecting due to error...');
      window.location.href = '/';
    }
  }, [session, status]); // Add dependencies

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