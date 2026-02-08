import { useState } from 'react';
import { BrandDNA } from '../types';
import Link from 'next/link';
import AccountLinker from './AccountLinker';
import OnboardingSteps from './steps';

export default function OnboardingPage() {
  const [url, setUrl] = useState('');
  const [prompt, setPrompt] = useState('');
  const [dna, setDna] = useState<BrandDNA | null>(null);

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
    <div className="max-w-xl mx-auto py-12">
      <h1 className="text-3xl font-bold mb-8">Onboarding: Brand DNA Extraction</h1>
      <div className="bg-zinc-800 rounded-xl p-6 shadow-lg flex flex-col gap-4">
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
      <OnboardingSteps />
      <AccountLinker />
    </div>
  );
}
