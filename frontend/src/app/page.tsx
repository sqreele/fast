'use client';

import { signIn, signOut, useSession } from "next-auth/react";

export default function Dashboard() {
  const { data: session } = useSession();

  return (
    <main className="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-indigo-100 to-white">
      <div className="w-full max-w-2xl mt-10 p-8 bg-white rounded-2xl shadow-lg">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold text-indigo-700">PM System Dashboard</h1>
          {!session ? (
            <button
              onClick={() => signIn()}
              className="px-6 py-2 bg-indigo-600 text-white rounded-lg shadow hover:bg-indigo-700 transition"
            >
              Login
            </button>
          ) : (
            <button
              onClick={() => signOut()}
              className="px-6 py-2 bg-gray-200 text-indigo-700 rounded-lg shadow hover:bg-gray-300 transition"
            >
              Logout
            </button>
          )}
        </div>

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