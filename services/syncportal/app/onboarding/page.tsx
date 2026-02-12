import { useState } from 'react';
import { useRouter } from 'next/router';
import { BrandDNA } from '../types';
import Link from 'next/link';
import AccountLinker from './AccountLinker';
import OnboardingSteps from './steps';

  const router = useRouter();
  const [url, setUrl] = useState('');
  const [prompt, setPrompt] = useState('');
  const [dna, setDna] = useState<BrandDNA | null>(null);

  // Capture service slug from query or referrer
  const serviceSlug = router.query.service as string || '';
  const serviceName = serviceSlug ? serviceSlug.replace(/-/g, ' ') : 'Agent';

  const handleSubmit = async () => {
    // Mock: Call SyncScrape or Prompt Engine
    setDna({
      brandName: 'Rare Beauty',
      voice: 'Inclusive, authentic, uplifting',
      valueProps: ['Cruelty-free', 'Mental health advocacy', 'Accessible beauty'],
      visualLanguage: { primaryHex: '#F7CAC9', secondaryHex: '#92A8D1' },
      audience: 'Gen-Z, Millennial, High-Intent Beauty Shoppers',
      tone: 'Empowering',
      complexity: 'Conversational',
      socialProof: ['4.8/5 reviews', 'Sephora Best Seller'],
    });
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-white flex flex-col items-center justify-center">
      <div className="w-full max-w-xl px-8 py-16 text-center">
        <h1 className="font-calsans text-4xl text-cyan-400 mb-6">
          Activating the {serviceName} for your Brand DNA.
        </h1>
        <ol className="text-left font-intertight text-lg mb-8 list-decimal list-inside">
          <li>Brand Ingest: Upload your logo, colors, and voice.</li>
          <li>API Integration: Connect Ad/CRM accounts (Meta, Google, Salesforce, HubSpot).</li>
          <li>Wallet Setup: Link PayPal or Digital Wallet for OaaS billing.</li>
          <li>Sovereign Agreement: Review and sign the performance contract.</li>
        </ol>
        <div className="bg-zinc-800 rounded-xl p-6 shadow-lg flex flex-col gap-4 mb-8">
          <label className="font-semibold">Paste your brand URL:</label>
          <input
            type="text"
            value={url}
            onChange={e => setUrl(e.target.value)}
            className="bg-zinc-700 rounded px-4 py-2 text-white"
            placeholder="https://yourbrand.com"
          />
          <label className="font-semibold mt-4">Or enter a strategic prompt:</label>
          <textarea
            value={prompt}
            onChange={e => setPrompt(e.target.value)}
            className="bg-zinc-700 rounded px-4 py-2 text-white"
            placeholder="Describe your brand vision..."
          />
          <button className="bg-blue-500 text-white px-4 py-2 rounded mt-4" onClick={handleSubmit}>
            Extract Brand DNA
          </button>
          {dna && (
            <div className="mt-6 bg-zinc-900 rounded p-4">
              <div className="font-bold text-lg mb-2">Extracted Brand DNA</div>
              <pre className="text-xs text-slate-300 whitespace-pre-wrap">{JSON.stringify(dna, null, 2)}</pre>
              <Link href="/dashboard" className="mt-4 block text-blue-400 hover:underline">Go to Dashboard</Link>
            </div>
          )}
        </div>
        <button className="bg-cyan-400 text-zinc-950 font-bold px-8 py-4 rounded-xl text-xl shadow-lg hover:bg-cyan-300 transition mb-8">
          Begin Onboarding →
        </button>
        <OnboardingSteps />
        <AccountLinker />
      </div>
      <footer className="mt-16 text-xs text-zinc-500">
        SOC2 Type II • ISO 27001 • GDPR • Immutable Audit Logs • Integration Ecosystem: Shopify, Meta, Google, Salesforce, Stripe • © 2026 KIKI™ Enterprise Platform.
      </footer>
    </div>
  );
}
