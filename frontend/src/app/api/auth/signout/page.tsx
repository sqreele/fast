'use client';

import { useState } from 'react';
import { signOut } from 'next-auth/react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function SignOut() {
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleSignOut = async () => {
    setIsLoading(true);
    try {
      await signOut({ 
        redirect: false,
        callbackUrl: '/' 
      });
      router.push('/');
      router.refresh();
    } catch (error) {
      console.error('Sign out error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="flex items-center justify-center min-h-screen bg-gradient-to-br from-indigo-100 to-white px-4">
      <div className="auth-container">
        <div className="auth-header">
          <h1 className="auth-title">Sign Out</h1>
          <p className="auth-subtitle">Are you sure you want to sign out?</p>
        </div>

        <div className="auth-form">
          <button
            onClick={handleSignOut}
            className={`btn-auth btn-logout ${isLoading ? 'btn-loading' : ''}`}
            disabled={isLoading}
          >
            {isLoading ? 'Signing out...' : 'Yes, Sign Out'}
          </button>
          
          <Link href="/" className="btn-auth btn-secondary">
            Cancel
          </Link>
        </div>
      </div>
    </main>
  );
}