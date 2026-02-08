import { useState } from 'react';
import { useOnboardingStore } from './useOnboardingStore';

const PROVIDERS = [
  { id: 'shopify', name: 'Shopify', type: 'CRM' },
  { id: 'meta', name: 'Meta Ads', type: 'Ad Platform' },
  { id: 'google', name: 'Google Ads', type: 'Ad Platform' },
  { id: 'hubspot', name: 'HubSpot', type: 'CRM' },
  { id: 'klaviyo', name: 'Klaviyo', type: 'CRM' },
  { id: 'tiktok', name: 'TikTok Ads', type: 'Ad Platform' },
  { id: 'linkedin', name: 'LinkedIn Ads', type: 'Ad Platform' },
];

export default function AccountLinker() {
  const [status, setStatus] = useState<Record<string, boolean>>({});
  const [loading, setLoading] = useState<string | null>(null);
  const setAccount = useOnboardingStore(s => s.setAccount);

  const checkStatus = async (provider: string) => {
    const res = await fetch(`/api/onboarding/check-account?provider=${provider}`);
    const data = await res.json();
    setStatus(s => ({ ...s, [provider]: data.linked }));
    setAccount(provider, data.linked);
  };

  const linkAccount = async (provider: string) => {
    setLoading(provider);
    const res = await fetch('/api/onboarding/link-account', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ provider }),
    });
    const data = await res.json();
    window.open(data.url, '_blank');
    setLoading(null);
    // Optionally poll/check status after OAuth
  };

  return (
    <div className="bg-zinc-800 rounded-xl p-6 shadow-lg mt-8">
      <h2 className="text-xl font-semibold mb-4">Connect Your Ad & CRM Accounts</h2>
      <ul className="flex flex-col gap-4">
        {PROVIDERS.map(p => (
          <li key={p.id} className="flex items-center gap-4">
            <span className="w-32 font-medium">{p.name}</span>
            <button
              className={`px-4 py-2 rounded ${status[p.id] ? 'bg-green-600 text-white' : 'bg-blue-500 text-white'}`}
              onClick={() => linkAccount(p.id)}
              disabled={loading === p.id || status[p.id]}
            >
              {status[p.id] ? 'Connected' : loading === p.id ? 'Connecting...' : 'Connect'}
            </button>
            <button
              className="text-xs text-slate-400 underline ml-2"
              onClick={() => checkStatus(p.id)}
            >
              Check Status
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
