'use client';

import { useEffect } from 'react';
import { signOut } from 'next-auth/react';
import { useRouter } from 'next/navigation';

export default function SignOut() {
  const router = useRouter();

  useEffect(() => {
    const performSignOut = async () => {
      try {
        // Sign out using NextAuth
        await signOut({ 
          callbackUrl: '/signin',
          redirect: false 
        });
        
        // Redirect to signin page
        router.push('/signin');
      } catch (error) {
        console.error('Sign out error:', error);
        // Fallback redirect
        router.push('/signin');
      }
    };

    performSignOut();
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Signing out...</p>
      </div>
    </div>
  );
} 