import { useSession, signOut, getSession } from 'next-auth/react';
import { useCallback } from 'react';
import { authApi } from '../services/api';
import { getAuthBaseUrl, getSignoutCallbackUrl } from '../lib/auth-utils';

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
      
      // Get the proper callback URL for signout
      const callbackUrl = getSignoutCallbackUrl();
      console.log('Using callback URL for signout:', callbackUrl);
      
      // Then clear the NextAuth session with proper URL handling
      const signOutResult = await signOut({ 
        callbackUrl,
        redirect: false  // Keep false to prevent automatic redirect with invalid URLs
      });
      
      console.log('✅ NextAuth signOut completed:', signOutResult);
      
      // Manual redirect after successful signOut with proper URL
      console.log('🔄 Redirecting to signin page...');
      if (typeof window !== 'undefined') {
        window.location.href = getSignoutCallbackUrl();
      }
      
    } catch (error) {
      console.error('❌ Logout error:', error);
      if (error instanceof Error) {
        console.error('Error details:', {
          message: error.message,
          name: error.name,
          stack: error.stack?.substring(0, 200)
        });
      }
      
      // Even if there's an error, try to redirect to signin page
      console.log('🔄 Fallback: redirecting to signin page...');
      if (typeof window !== 'undefined') {
        window.location.href = getSignoutCallbackUrl();
      }
    }
  }, [session, status]);

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