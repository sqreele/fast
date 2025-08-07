import type { NextAuthOptions } from 'next-auth'
import CredentialsProvider from 'next-auth/providers/credentials'

export const authOptions: NextAuthOptions = {
  providers: [
    CredentialsProvider({
      name: 'credentials',
      credentials: {
        username: { label: "Username", type: "text" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials) {
        if (!credentials?.username || !credentials?.password) {
          return null
        }

        try {
          const response = await fetch(`${process.env.BACKEND_URL || 'http://fastapi:8000'}/api/v1/auth/login`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              username: credentials.username,
              password: credentials.password,
            }),
          })

          if (!response.ok) {
            return null
          }

          const user = await response.json()
          
          return {
            id: user.id.toString(),
            name: user.name,
            email: user.email,
            username: user.username,
            role: user.role,
            accessToken: user.token,
          }
        } catch (error) {
          console.error('Authentication error:', error)
          return null
        }
      }
    })
  ],
  pages: {
    signIn: '/signin',
    signOut: '/signout',
    error: '/auth/error',
  },
  callbacks: {
    async jwt({ token, user, account }) {
      if (account && user) {
        token.accessToken = (user as any).accessToken;
        token.role = (user as any).role;
        token.username = (user as any).username;
      }
      return token;
    },
    async session({ session, token }) {
      if (token) {
        session.user.id = token.sub || '';
        session.user.role = token.role;
        session.user.username = token.username;
        session.accessToken = token.accessToken;
      }
      return session;
    },
    async redirect({ url, baseUrl }) {
      // Add logging for debugging redirect issues
      console.log('NextAuth redirect called:', { url, baseUrl });
      
      // Always redirect to baseUrl to avoid invalid URLs
      if (url.startsWith('/')) {
        const redirectUrl = `${baseUrl}${url}`;
        console.log('Redirecting to:', redirectUrl);
        return redirectUrl;
      }
      
      // Check if URL is from the same origin
      try {
        if (new URL(url).origin === baseUrl) {
          console.log('Redirecting to same origin URL:', url);
          return url;
        }
      } catch (error) {
        console.warn('Invalid URL in redirect:', url, error);
      }
      
      // Ensure we don't redirect to localhost in production
      if (process.env.NODE_ENV === 'production' && baseUrl.includes('localhost')) {
        const productionUrl = process.env.NEXTAUTH_URL || 'http://206.189.89.239';
        console.log('Production environment detected, redirecting to:', productionUrl);
        return productionUrl;
      }
      
      console.log('Final redirect to baseUrl:', baseUrl);
      return baseUrl;
    },
  },
  secret: process.env.NEXTAUTH_SECRET || 'your-secret-key-change-in-production',
  session: {
    strategy: 'jwt',
  },
}