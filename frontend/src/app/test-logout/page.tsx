'use client';

import { signIn, signOut, useSession, getSession } from "next-auth/react";
import { useState } from "react";

export default function TestLogout() {
  const { data: session } = useSession();
  const [logs, setLogs] = useState<string[]>([]);

  const addLog = (message: string) => {
    setLogs(prev => [...prev, `${new Date().toISOString()}: ${message}`]);
  };

  const testLogout = async () => {
    addLog('Starting logout test...');
    
    try {
      const session = await getSession();
      addLog(`Session found: ${session ? 'Yes' : 'No'}`);
      
      if (session?.accessToken) {
        addLog(`Access token found: ${session.accessToken.substring(0, 20)}...`);
        
        // Test different logout URLs
        const testUrls = [
          '/api/v1/auth/logout',
          'http://localhost:8000/api/v1/auth/logout',
          'http://fastapi:8000/api/v1/auth/logout'
        ];
        
        for (const url of testUrls) {
          try {
            addLog(`Testing URL: ${url}`);
            const response = await fetch(url, {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${session.accessToken}`,
                'Content-Type': 'application/json'
              }
            });
            
            addLog(`Response status: ${response.status}`);
            if (response.ok) {
              const data = await response.text();
              addLog(`Response data: ${data}`);
              break;
            }
          } catch (error) {
            addLog(`Error with ${url}: ${error}`);
          }
        }
      } else {
        addLog('No access token found in session');
      }
      
      // Test NextAuth signOut
      addLog('Calling NextAuth signOut...');
      await signOut({ 
        callbackUrl: '/',
        redirect: false 
      });
      addLog('NextAuth signOut completed');
      
    } catch (error) {
      addLog(`Error during logout test: ${error}`);
    }
  };

  const clearLogs = () => {
    setLogs([]);
  };

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Logout Test Page</h1>
      
      <div className="mb-4">
        <p>Session status: {session ? 'Authenticated' : 'Not authenticated'}</p>
        {session && (
          <p>User: {session.user?.name || session.user?.email}</p>
        )}
      </div>
      
      <div className="mb-4 space-x-4">
        <button
          onClick={testLogout}
          className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Test Logout
        </button>
        
        <button
          onClick={clearLogs}
          className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
        >
          Clear Logs
        </button>
      </div>
      
      <div className="bg-gray-100 p-4 rounded">
        <h2 className="font-bold mb-2">Logs:</h2>
        <div className="max-h-96 overflow-y-auto">
          {logs.map((log, index) => (
            <div key={index} className="text-sm font-mono mb-1">
              {log}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
} 