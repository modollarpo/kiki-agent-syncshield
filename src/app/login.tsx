"use client";
import { useState } from "react";
import { signIn } from "next-auth/react";

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    const res = await signIn("credentials", {
      redirect: false,
      username,
      password,
    });
    if (!res?.ok) setError("Invalid credentials");
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#020617]">
      <form onSubmit={handleLogin} className="bg-slate-900/70 p-8 rounded-xl shadow-xl flex flex-col gap-4 w-80">
        <h2 className="text-xl font-bold text-white mb-2">Login to KIKI Command Center</h2>
        <input
          className="rounded px-3 py-2 bg-slate-800 text-white"
          placeholder="Username"
          value={username}
          onChange={e => setUsername(e.target.value)}
          required
        />
        <input
          className="rounded px-3 py-2 bg-slate-800 text-white"
          placeholder="Password"
          type="password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          required
        />
        {error && <div className="text-red-400 text-sm">{error}</div>}
        <button className="bg-emerald-600 text-white rounded py-2 font-semibold hover:opacity-80" type="submit">
          Login
        </button>
      </form>
    </div>
  );
}
