'use client';

import { signIn, signOut } from "next-auth/react";
import { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "../hooks/useAuth";

interface SystemStatus {
  status: string;
}

export default function Dashboard() {
  const { session, isAuthenticated, logout } = useAuth();
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);

  const checkHealth = async () => {
    try {
      const response = await fetch('/health', {
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'Cache-Control': 'no-cache'
        }
      });
      if (response.ok) {
        const text = await response.text();
        console.log('Health check raw response:', text);
        console.log('Response headers:', Object.fromEntries(response.headers.entries()));
        
        // Handle both JSON and plain text responses
        if (text.trim() === 'healthy') {
          // If we get plain text "healthy", create a mock status object
          setSystemStatus({ status: 'healthy' });
        } else {
          try {
            const data = JSON.parse(text) as SystemStatus;
            setSystemStatus(data);
          } catch (parseError) {
            console.error('Failed to parse health check response as JSON:', text);
            console.error('Parse error:', parseError);
            // Fallback: if we get any response, assume healthy
            setSystemStatus({ status: 'unknown' });
          }
        }
      } else {
        console.error('Health check failed with status:', response.status);
      }
    } catch (error) {
      console.error('Health check failed:', error);
    }
  };

  const fetchProjects = async () => {
    // Placeholder for future implementation
    console.log('Fetching projects...');
  };

  const fetchTickets = async () => {
    // Placeholder for future implementation
    console.log('Fetching tickets...');
  };

  useEffect(() => {
    checkHealth();
    fetchProjects();
    fetchTickets();
  }, []);

  return (
    <main className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-indigo-100 to-white">
      <div className="w-full max-w-2xl mt-10 p-8 bg-white rounded-2xl shadow-lg">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold text-indigo-700">PM System Dashboard</h1>
          {!session ? (
            <div className="flex gap-3">
              <button
                onClick={() => signIn()}
                className="px-6 py-2 bg-indigo-600 text-white rounded-lg shadow hover:bg-indigo-700 transition"
              >
                Login
              </button>
              <Link
                href="/register"
                className="px-6 py-2 bg-green-600 text-white rounded-lg shadow hover:bg-green-700 transition text-center inline-block"
              >
                Register
              </Link>
            </div>
          ) : (
            <button
              onClick={() => logout()}
              className="px-6 py-2 bg-gray-200 text-indigo-700 rounded-lg shadow hover:bg-gray-300 transition"
            >
              Sign Out
            </button>
          )}
        </div>

        {/* System Status */}
        {systemStatus && (
          <div className="mb-4 p-2 bg-green-100 text-green-800 rounded">
            System Status: {systemStatus.status}
          </div>
        )}

        {/* Action Row */}
        <div className="flex flex-wrap gap-4 justify-center mb-8">
          <button className="px-4 py-2 bg-blue-500 text-white rounded-lg shadow hover:bg-blue-600 transition">
            Message Support
          </button>
          <button className="px-4 py-2 bg-green-500 text-white rounded-lg shadow hover:bg-green-600 transition">
            Upscale
          </button>
          <button className="px-4 py-2 bg-yellow-500 text-white rounded-lg shadow hover:bg-yellow-600 transition">
            Maintenance
          </button>
        </div>

        {/* Main content */}
        <div className="text-center text-gray-600">
          {session ? (
            <p>Welcome, <span className="font-semibold">{session.user?.name || session.user?.email}</span>!</p>
          ) : (
            <p>Please log in to access your dashboard features.</p>
          )}
        </div>
      </div>
    </main>
  );
}