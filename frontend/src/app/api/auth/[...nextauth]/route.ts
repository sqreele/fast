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
          const res = await fetch(`${process.env.BACKEND_URL || "http://localhost:8000"}/api/v1/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              username: credentials.username,
              password: credentials.password
            })
          });

          if (!res.ok) return null;

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
    error: '/auth/error', // Use our custom error page
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
    }
  }
});

export { handler as GET, handler as POST };