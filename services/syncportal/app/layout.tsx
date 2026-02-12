import './globals.css';
import { SEO_CONFIG } from './components/seo/SEO_CONFIG';
import { NextSeo } from 'next-seo';
import { Sidebar } from './components/dashboard/Sidebar';
import { MegaMenu } from './components/dashboard/MegaMenu';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head></head>
      <body className="bg-zinc-900 text-slate-100 min-h-screen">
        {/* SEO is handled via metadata or page-level components in App Router. Removed NextSeo to fix hook errors. */}
        <Sidebar />
        <MegaMenu />
        <main className="pl-64 pt-8 pb-8 pr-8">
          {children}
        </main>
      </body>
    </html>
  );
}
