"use client";
"use client";
import Link from "next/link";
export default function Home() {
  return (
    <main className="flex flex-col items-center justify-center min-h-screen bg-slate-950">
      <h1 className="text-4xl font-bold text-emerald-400 mb-8">KIKI Agent™ Command Center</h1>
      <Link href="/onboarding">
        <button className="px-8 py-4 bg-emerald-600 text-white rounded-xl text-xl font-semibold shadow-lg hover:bg-emerald-700 transition-all">
          Start OaaS Onboarding
        </button>
      </Link>
    </main>
  );
}


