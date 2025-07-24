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
          return null;
        }

        try {
          // This will use the BACKEND_URL environment variable
          const res = await fetch(`${process.env.BACKEND_URL}/api/v1/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              username: credentials.username,
              password: credentials.password
            })
          });

          if (!res.ok) {
            console.error('Login failed:', res.status, res.statusText);
            return null;
          }

          const user = await res.json() as ExtendedUser;
          if (user && user.token) {
            return {
              id: user.id || user.email || user.name || "unknown",
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
    signIn: '/api/auth/signin',
    error: '/api/auth/error',  // This should fix the 404 on /auth/error
  },
  session: {
    strategy: "jwt"
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
  debug: process.env.NODE_ENV === 'development',
});

export { handler as GET, handler as POST };