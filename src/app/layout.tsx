import './globals.css';
import SovereignHeader from './SovereignHeader';
import Footer from '../components/Footer';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <SovereignHeader />
        <main className="bg-zinc-950 text-zinc-100 min-h-screen font-intertight">
          {children}
        </main>
        <Footer />
      </body>
    </html>
  );
}
