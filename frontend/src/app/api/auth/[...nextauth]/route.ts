import NextAuth from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";
import type { User, Session } from "next-auth";
import type { JWT } from "next-auth/jwt";

interface ExtendedUser extends User {
  token?: string;
}

const handler = NextAuth({
  providers: [
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        username: { label: "Username", type: "text" },
        password: { label: "Password", type: "password" }
      },
      async authorize(credentials): Promise<ExtendedUser | null> {
        if (!credentials?.username || !credentials?.password) {
          console.error('Missing credentials');
          return null;
        }

        try {
          // Use internal service name for backend communication
          const backendUrl = process.env.BACKEND_URL || 'http://fastapi:8000';
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
            const errorText = await res.text();
            console.error('Login failed:', res.status, res.statusText, errorText);
            return null;
          }

          const user = await res.json() as ExtendedUser;
          console.log('Login successful for user:', user.name || user.email);
          
          if (user && (user.token || user.id || user.email)) {
            return {
              id: user.id?.toString() || user.email || user.name || "unknown",
              name: user.name,
              email: user.email,
              token: user.token
            };
          }
        } catch (error) {
          console.error("Auth error:", error);
        }
        return null;
      }
    })
  ],
  pages: {
    signIn: '/api/auth/signin',  // Fixed typo
    error: '/api/auth/error',
    signOut: '/api/auth/signout'
  },
  session: {
    strategy: "jwt",
    maxAge: 24 * 60 * 60, // 24 hours
  },
  callbacks: {
    async jwt({ token, user }: { token: JWT; user?: ExtendedUser }): Promise<JWT> {
      if (user) {
        token.accessToken = user.token;
        token.user = user;
      }
      return token;
    },
    async session({ session, token }: { session: Session; token: JWT }): Promise<Session> {
      return {
        ...session,
        accessToken: token.accessToken,
        user: {
          ...session.user,
          id: token.user?.id || session.user?.email || "unknown"
        }
      };
    },
    async redirect({ url, baseUrl }) {
      // Ensure redirects stay within the app
      if (url.startsWith("/")) return `${baseUrl}${url}`;
      if (new URL(url).origin === baseUrl) return url;
      return baseUrl;
    }
  },
  secret: process.env.NEXTAUTH_SECRET || 'fallback-secret-key-for-development',
  debug: process.env.NODE_ENV === 'development',
});

export { handler as GET, handler as POST };