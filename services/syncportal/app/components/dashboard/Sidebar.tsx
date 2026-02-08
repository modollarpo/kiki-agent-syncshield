import { LucideIcon } from 'lucide-react';
import Link from 'next/link';

export function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-zinc-950 border-r border-zinc-800 flex flex-col">
      <div className="p-6 text-xl font-bold">KIKI Agent™</div>
      <nav className="flex-1 flex flex-col gap-4 p-4">
        <Link href="/dashboard">Dashboard</Link>
        <Link href="/learning-hub">Learning Hub</Link>
        <Link href="/blog">Blog</Link>
        <Link href="/settings">Settings</Link>
      </nav>
    </aside>
  );
}
