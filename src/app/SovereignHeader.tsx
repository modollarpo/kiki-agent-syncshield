import Link from 'next/link';

export default function SovereignHeader() {
  return (
    <header className="w-full border-b border-zinc-800 py-4 px-8 flex items-center justify-between bg-zinc-950">
      <div className="text-2xl font-bold text-cyan-400 tracking-tight">KIKI Agent™</div>
      <nav className="flex gap-6">
        <Link href="/dashboard" className="text-white hover:text-cyan-400 font-intertight">Dashboard</Link>
        <Link href="/learning-hub" className="text-white hover:text-cyan-400 font-intertight">Learning Hub</Link>
        <Link href="/onboarding" className="text-white hover:text-cyan-400 font-intertight">Onboarding</Link>
      </nav>
    </header>
  );
}
