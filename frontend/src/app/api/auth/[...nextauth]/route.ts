// pages/api/auth/[...nextauth].js or app/api/auth/[...nextauth]/route.ts
import NextAuth from 'next-auth'
import type { NextAuthOptions } from 'next-auth'

export const authOptions: NextAuthOptions = {
  providers: [
    // Your providers here
  ],
  pages: {
    signIn: '/login',  // Use your custom login page
    signOut: '/logout', // Use your custom logout page
    error: '/auth/error',
  },
  callbacks: {
    async jwt({ token, user, account }) {
      if (account && user) {
        token.accessToken = account.access_token;
      }
      return token;
    },
    async session({ session, token }) {
      session.accessToken = token.accessToken;
      return session;
    },
    async redirect({ url, baseUrl }) {
      // Always redirect to baseUrl to avoid invalid URLs
      if (url.startsWith('/')) return `${baseUrl}${url}`;
      if (new URL(url).origin === baseUrl) return url;
      return baseUrl;
    },
  },
  // CRITICAL: Ensure these URLs are correct
  url: process.env.NEXTAUTH_URL,
  secret: process.env.NEXTAUTH_SECRET,
}

export default NextAuth(authOptions)
