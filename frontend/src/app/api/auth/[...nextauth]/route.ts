import NextAuth from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
import type { User, Session } from "next-auth";
import type { JWT } from "next-auth/jwt";

interface ExtendedUser extends User {
  token?: string;
  role?: string;
  refreshToken?: string;
  accessTokenExpires?: number;
}

interface BackendResponse {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  token: string;
  name: string;
}

const handler = NextAuth({
  providers: [
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        username: { label: "Username", type: "text", placeholder: "Enter your username" },
        password: { label: "Password", type: "password", placeholder: "Enter your password" }
      },
      async authorize(credentials): Promise<ExtendedUser | null> {
        if (!credentials?.username || !credentials?.password) {
          console.error('Missing credentials');
          throw new Error('Please enter both username and password');
        }

        try {
          // Get backend URL from environment or use default
          const backendUrl = process.env.NEXTAUTH_BACKEND_URL || 
                           process.env.BACKEND_URL || 
                           process.env.NEXT_PUBLIC_BACKEND_URL ||
                           'http://localhost:8000';
          
          console.log('Attempting login with backend:', backendUrl);
          
          const res = await fetch(`${backendUrl}/api/v1/auth/login`, {
            method: "POST",
            headers: { 
              "Content-Type": "application/json",
              "Accept": "application/json"
            },
            body: JSON.stringify({
              username: credentials.username,
              password: credentials.password
            })
          });

          console.log('Login response status:', res.status);

          if (!res.ok) {
            let errorMessage = 'Authentication failed';
            try {
              const errorData = await res.json();
              errorMessage = errorData.detail || errorData.message || errorMessage;
            } catch {
              const errorText = await res.text();
              console.error('Login failed:', res.status, res.statusText, errorText);
            }
            throw new Error(errorMessage);
          }

          const backendUser = await res.json() as BackendResponse;
          console.log('Login successful for user:', backendUser.name || backendUser.email);
          
          if (backendUser && backendUser.token) {
            // Convert backend response to NextAuth user format
            return {
              id: backendUser.id.toString(),
              name: backendUser.name || `${backendUser.first_name} ${backendUser.last_name}`,
              email: backendUser.email,
              token: backendUser.token,
              role: backendUser.role,
              // Set token expiration (24 hours from now)
              accessTokenExpires: Date.now() + 24 * 60 * 60 * 1000
            };
          }
          
          throw new Error('Invalid response from server');
        } catch (error) {
          console.error("Auth error:", error);
          // Re-throw the error so NextAuth can handle it properly
          throw error;
        }
      }
    })
  ],
  pages: {
    signIn: '/api/auth/signin',
    error: '/api/auth/error',
    signOut: '/api/auth/signout'
  },
  session: {
    strategy: "jwt",
    maxAge: 24 * 60 * 60, // 24 hours
    updateAge: 60 * 60, // Update session every hour
  },
  callbacks: {
    async jwt({ token, user, account }): Promise<JWT> {
      // Initial sign in
      if (account && user) {
        const extendedUser = user as ExtendedUser;
        return {
          ...token,
          accessToken: extendedUser.token,
          accessTokenExpires: extendedUser.accessTokenExpires,
          refreshToken: extendedUser.refreshToken,
          user: {
            id: user.id,
            name: user.name,
            email: user.email,
            role: extendedUser.role
          }
        };
      }

      // Return previous token if the access token has not expired yet
      if (token.accessTokenExpires && Date.now() < token.accessTokenExpires) {
        return token;
      }

      // Access token has expired, try to update it
      // In a real implementation, you would refresh the token here
      console.log('Access token expired, would refresh here');
      return token;
    },
    
    async session({ session, token }): Promise<Session> {
      return {
        ...session,
        accessToken: token.accessToken,
        user: {
          ...session.user,
          id: token.user?.id || session.user?.email || "unknown",
          role: token.user?.role
        }
      };
    },
    
    async redirect({ url, baseUrl }) {
      // Allows relative callback URLs
      if (url.startsWith("/")) return `${baseUrl}${url}`;
      // Allows callback URLs on the same origin
      else if (new URL(url).origin === baseUrl) return url;
      return baseUrl;
    }
  },
  events: {
    async signIn({ user, account, profile }) {
      console.log('User signed in:', user.email);
    },
    async signOut({ session, token }) {
      console.log('User signed out');
      // Here you could call your backend logout endpoint
      try {
        const backendUrl = process.env.NEXTAUTH_BACKEND_URL || 
                         process.env.BACKEND_URL || 
                         process.env.NEXT_PUBLIC_BACKEND_URL ||
                         'http://localhost:8000';
        
        await fetch(`${backendUrl}/api/v1/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token?.accessToken}`,
            'Content-Type': 'application/json'
          }
        });
      } catch (error) {
        console.error('Error during backend logout:', error);
      }
    }
  },
  secret: process.env.NEXTAUTH_SECRET || 'fallback-secret-key-for-development-only',
  debug: process.env.NODE_ENV === 'development',
});

export { handler as GET, handler as POST };