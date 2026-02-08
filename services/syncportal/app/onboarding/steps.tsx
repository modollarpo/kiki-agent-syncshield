import { useState } from 'react';
import Link from 'next/link';
import { BrandDNA } from '../types';
import { simulateSyncTwin } from '../dashboard/client/synctwin-grpc';

const steps = [
  'Paste your brand URL or enter a prompt',
  'Extract Brand DNA',
  'Connect Ad Platforms & CRM',
  'Generate creatives and ad copy',
  'Simulate campaign with SyncTwin™',
  'Review simulation results',
  'Launch campaign',
];

export default function OnboardingSteps() {
  const [current, setCurrent] = useState(0);
  const [dna, setDna] = useState<BrandDNA | null>(null);
  const [sim, setSim] = useState<any | null>(null);
  const [adConnected, setAdConnected] = useState(false);
  const [crmConnected, setCrmConnected] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleNext = async () => {
    setError(null);
    try {
      if (current === 1) {
        // Extract Brand DNA (real API call)
        const res = await fetch('/api/onboarding/extract-dna', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: '', prompt: '' }), // TODO: wire to user input
        });
        if (!res.ok) throw new Error('Failed to extract Brand DNA');
        const data = await res.json();
        setDna(data);
      }
      if (current === 2) {
        // Generate creatives (real API call)
        const res = await fetch('/api/onboarding/generate-creatives', { method: 'POST' });
        if (!res.ok) throw new Error('Failed to generate creatives');
        const data = await res.json();
        // Optionally display creatives/adCopy
      }
      if (current === 3) {
        // Simulate campaign (real gRPC call)
        const response = await fetch('/api/synctwin/simulate', { method: 'POST' });
        if (!response.ok) throw new Error('Simulation failed');
        const data = await response.json();
        setSim(data);
      }
      setCurrent(current + 1);
    } catch (err: any) {
      setError(err.message || 'An error occurred');
    }
  };

  const handleAdConnect = async (platform: string) => {
    setLoading(true);
    try {
      await fetch('/api/onboarding/oauth-ad', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ platform }),
      });
      setAdConnected(true);
    } finally {
      setLoading(false);
    }
  };
  const handleCrmConnect = async (platform: string) => {
    setLoading(true);
    try {
      await fetch('/api/onboarding/oauth-crm', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ platform }),
      });
      setCrmConnected(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto py-12">
      <h1 className="text-3xl font-bold mb-8">Onboarding Steps</h1>
      <ol className="list-decimal pl-6 mb-8">
        {steps.map((step, idx) => (
          <li key={step} className={idx === current ? 'font-bold text-blue-400 animate-pulse' : 'text-slate-400'}>
            {step}
          </li>
        ))}
      </ol>
      {current === 2 && (
        <div className="mb-4 flex flex-col gap-2">
          <button className={`px-4 py-2 rounded mr-2 ${adConnected ? 'bg-green-600' : 'bg-blue-500 text-white'}`} onClick={() => handleAdConnect('meta')} disabled={adConnected || loading}>
            {adConnected ? 'Ad Platform Connected' : 'Connect Meta Ad Platform'}
          </button>
          <button className={`px-4 py-2 rounded ${crmConnected ? 'bg-green-600' : 'bg-blue-500 text-white'}`} onClick={() => handleCrmConnect('hubspot')} disabled={crmConnected || loading}>
            {crmConnected ? 'CRM Connected' : 'Connect HubSpot CRM'}
          </button>
        </div>
      )}
      {error && (
        <div className="mt-4 text-red-400 font-semibold">{error}</div>
      )}
      <button className={`bg-blue-500 text-white px-4 py-2 rounded shadow-lg transition-all ${current < steps.length - 1 ? 'hover:bg-blue-600' : 'bg-green-600 hover:bg-green-700'}`} onClick={handleNext} disabled={current >= steps.length - 1}>
        {current < steps.length - 1 ? 'Next Step' : 'Done'}
      </button>
      {dna && (
        <div className="mt-6 bg-zinc-900 rounded p-4">
          <div className="font-bold text-lg mb-2">Extracted Brand DNA</div>
          <pre className="text-xs text-slate-300 whitespace-pre-wrap">{JSON.stringify(dna, null, 2)}</pre>
        </div>
      )}
      {sim && (
        <div className="mt-6 bg-zinc-900 rounded p-4">
          <div className="font-bold text-lg mb-2">SyncTwin™ Simulation Result</div>
          <div>Confidence Score: <span className="font-bold">{sim.confidenceScore}</span></div>
          <div>Risk Profile: <span className="font-bold">{sim.riskProfile}</span></div>
          <div>Projected Net Profit Uplift: <span className="font-bold">${sim.projectedNetProfitUplift}</span></div>
        </div>
      )}
      {current === steps.length - 1 && (
        <Link href="/dashboard" className="mt-8 block text-blue-400 hover:underline">Go to Dashboard</Link>
      )}
    </div>
  );
}
