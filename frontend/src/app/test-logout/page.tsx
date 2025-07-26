'use client';

import { useState } from "react";
import { useAuth } from "../../hooks/useAuth";
import { authApi } from "../../services/api";

export default function TestLogout() {
  const { session, isAuthenticated, logout } = useAuth();
  const [logs, setLogs] = useState<string[]>([]);
  const [isTestingLogout, setIsTestingLogout] = useState(false);

  const addLog = (message: string) => {
    setLogs(prev => [...prev, `${new Date().toISOString()}: ${message}`]);
  };

  const testLogout = async () => {
    if (isTestingLogout) return;
    
    setIsTestingLogout(true);
    addLog('Starting comprehensive logout test...');
    
    try {
      addLog(`Session found: ${session ? 'Yes' : 'No'}`);
      addLog(`Is authenticated: ${isAuthenticated}`);
      
      if (session?.accessToken) {
        addLog(`Access token found: ${session.accessToken.substring(0, 20)}...`);
        
        // Test backend logout directly
        try {
          addLog('Testing direct backend logout...');
          await authApi.logout();
          addLog('✅ Direct backend logout successful');
        } catch (error) {
          addLog(`❌ Direct backend logout failed: ${error}`);
        }
        
        // Test token verification after logout
        try {
          addLog('Testing token verification after logout...');
          await authApi.verifyToken();
          addLog('❌ Token still valid after logout (this is unexpected)');
        } catch (error) {
          addLog('✅ Token properly invalidated after logout');
        }
      } else {
        addLog('No access token found in session');
      }
      
      // Test the comprehensive logout function
      addLog('Testing comprehensive logout function...');
      await logout();
      addLog('✅ Comprehensive logout completed');
      
    } catch (error) {
      addLog(`❌ Error during logout test: ${error}`);
    } finally {
      setIsTestingLogout(false);
    }
  };

  const testBackendOnly = async () => {
    addLog('Testing backend-only logout...');
    try {
      await authApi.logout();
      addLog('✅ Backend logout successful');
    } catch (error) {
      addLog(`❌ Backend logout failed: ${error}`);
    }
  };

  const clearLogs = () => {
    setLogs([]);
  };

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Logout Test Page</h1>
      
      <div className="mb-4 p-4 border rounded">
        <h2 className="font-bold mb-2">Session Status:</h2>
        <p>Authentication status: {isAuthenticated ? 'Authenticated' : 'Not authenticated'}</p>
        {session && (
          <>
            <p>User: {session.user?.name || session.user?.email}</p>
            <p>Token: {session.accessToken ? `${session.accessToken.substring(0, 20)}...` : 'None'}</p>
          </>
        )}
      </div>
      
      <div className="mb-4 space-x-4">
        <button
          onClick={testLogout}
          disabled={isTestingLogout}
          className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50"
        >
          {isTestingLogout ? 'Testing...' : 'Test Complete Logout'}
        </button>
        
        <button
          onClick={testBackendOnly}
          className="px-4 py-2 bg-orange-600 text-white rounded hover:bg-orange-700"
        >
          Test Backend Logout Only
        </button>
        
        <button
          onClick={clearLogs}
          className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
        >
          Clear Logs
        </button>
      </div>
      
      <div className="bg-gray-100 p-4 rounded">
        <h2 className="font-bold mb-2">Test Logs:</h2>
        <div className="max-h-96 overflow-y-auto">
          {logs.length === 0 ? (
            <p className="text-gray-500 italic">No test logs yet. Click a test button to start.</p>
          ) : (
            logs.map((log, index) => (
              <div key={index} className={`text-sm font-mono mb-1 ${
                log.includes('✅') ? 'text-green-600' : 
                log.includes('❌') ? 'text-red-600' : 
                'text-gray-700'
              }`}>
                {log}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
} 