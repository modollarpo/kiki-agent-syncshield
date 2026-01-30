import NextAuth, { SessionStrategy } from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";

export const authOptions = {
  providers: [
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        username: { label: "Username", type: "text" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        // Replace with your backend auth API
        const res = await fetch("http://localhost:8000/auth/login", {
          method: "POST",
          body: JSON.stringify(credentials),
          headers: { "Content-Type": "application/json" },
        });
        const user = await res.json();
        if (res.ok && user) return user;
        return null;
      },
    }),
  ],
  session: { strategy: "jwt" as SessionStrategy },
  callbacks: {
    async jwt({ token, user }: { token: any; user?: any }) {
      if (user) token.user = user;
      return token;
    },
    async session({ session, token }: { session: any; token: any }) {
      session.user = token.user;
      return session;
    },
  },
};

const handler = NextAuth(authOptions);
export { handler as GET, handler as POST };
