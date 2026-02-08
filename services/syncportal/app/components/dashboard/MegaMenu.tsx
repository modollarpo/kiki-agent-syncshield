import Link from 'next/link';

export function MegaMenu() {
  return (
    <nav className="w-full bg-zinc-900 border-b border-zinc-800 flex items-center justify-between px-8 py-4">
      <div className="flex gap-6">
        <Link href="/">Home</Link>
        <Link href="/learning-hub">Learning Hub</Link>
        <Link href="/blog">Blog</Link>
        <Link href="/pricing">Pricing</Link>
        <Link href="/about">About</Link>
      </div>
      <div className="flex gap-4">
        <Link href="/dashboard">Client Dashboard</Link>
        <Link href="/onboarding">Onboarding</Link>
      </div>
    </nav>
  );
}
