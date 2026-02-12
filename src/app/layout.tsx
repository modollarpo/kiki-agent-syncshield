import './globals.css';
import SovereignHeader from './SovereignHeader';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <SovereignHeader />
        <main className="bg-zinc-950 text-white min-h-screen font-intertight">
          {children}
        </main>
      </body>
    </html>
  );
}
