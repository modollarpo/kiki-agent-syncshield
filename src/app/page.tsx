import Link from 'next/link';

export default function LandingPage() {
  return (
    <section className="w-full flex flex-col items-center justify-center py-24">
      <div className="max-w-4xl w-full px-8">
        <h1 className="text-5xl font-bold text-cyan-400 mb-8 font-intertight">Sovereign Noir: Enterprise OaaS Platform</h1>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-8 shadow-lg flex flex-col items-center">
            <span className="text-2xl font-bold text-cyan-400 mb-2">Dashboard</span>
            <p className="text-zinc-300 mb-4">Command Center for Net Profit Uplift, Attribution, and System Health.</p>
            <Link href="/dashboard" className="bg-cyan-400 text-zinc-950 font-bold px-6 py-2 rounded-lg shadow hover:bg-cyan-300 transition">Go to Dashboard</Link>
          </div>
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-8 shadow-lg flex flex-col items-center">
            <span className="text-2xl font-bold text-cyan-400 mb-2">Learning Hub</span>
            <p className="text-zinc-300 mb-4">Deep-dive guides, explainability, and OaaS best practices for enterprise teams.</p>
            <Link href="/learning-hub" className="bg-cyan-400 text-zinc-950 font-bold px-6 py-2 rounded-lg shadow hover:bg-cyan-300 transition">Explore Hub</Link>
          </div>
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-8 shadow-lg flex flex-col items-center">
            <span className="text-2xl font-bold text-cyan-400 mb-2">Onboarding</span>
            <p className="text-zinc-300 mb-4">Start your OaaS journey. Brand DNA extraction, CRM linking, and sovereign handshake.</p>
            <Link href="/onboarding" className="bg-cyan-400 text-zinc-950 font-bold px-6 py-2 rounded-lg shadow hover:bg-cyan-300 transition">Begin Onboarding</Link>
          </div>
        </div>
      </div>
    </section>
  );
}
