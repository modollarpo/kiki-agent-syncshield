"use client";
"use client";
import { signIn, signOut, useSession } from "next-auth/react";

export default function Header() {
  const { data: session } = useSession();
  return (
    <header className="flex items-center justify-between py-4 px-8 bg-slate-900/80 border-b border-slate-800 mb-8">
      <div className="text-2xl font-bold text-emerald-400">KIKI Command Center</div>
      <div>
        {session?.user ? (
          <>
            <span className="text-white mr-4">{session.user.name}</span>
            <button className="bg-emerald-600 text-white rounded px-4 py-2 font-semibold hover:opacity-80" onClick={() => signOut()}>Logout</button>
          </>
        ) : (
          <button className="bg-emerald-600 text-white rounded px-4 py-2 font-semibold hover:opacity-80" onClick={() => signIn()}>Login</button>
        )}
      </div>
    </header>
  );
}
