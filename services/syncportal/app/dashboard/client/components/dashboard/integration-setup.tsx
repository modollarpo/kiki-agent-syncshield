import { LucidePlug } from 'lucide-react';
import { useEffect, useState } from 'react';
import { fetchIntegrations } from '../../api/dashboard-data';
import { startOAuth } from '../../api/oauth';

type Integration = {
  name: string;
  status: 'connected' | 'not_connected';
  provider: string;
};

export function IntegrationSetup() {
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  useEffect(() => {
    fetchIntegrations().then(setIntegrations);
  }, []);

  return (
    <div className="bg-zinc-900 rounded-xl p-6 shadow-lg border border-zinc-800">
      <div className="flex items-center gap-2 mb-2">
        <LucidePlug className="w-5 h-5 text-sky-400" />
        <h2 className="text-lg font-bold">Integrations</h2>
      </div>
      <div className="space-y-3">
        {integrations.map((integration, i) => (
          <div key={i} className="flex items-center gap-4">
            <span className="text-zinc-200 font-medium">{integration.name}</span>
            <span className={`text-xs px-2 py-1 rounded-lg ${integration.status === 'connected' ? 'bg-green-700 text-green-100' : 'bg-zinc-700 text-zinc-300'}`}>
              {integration.status === 'connected' ? 'Connected' : 'Connect'}
            </span>
            {integration.status !== 'connected' && (
              <button className="ml-auto bg-sky-600 hover:bg-sky-700 text-white px-3 py-1 rounded-lg text-xs font-semibold" onClick={() => startOAuth(integration.provider)}>
                Connect
              </button>
            )}
          </div>
        ))}
      </div>
      <div className="mt-4 text-xs text-zinc-400">
        Connect your ad platforms and CRMs to unlock full KIKI OaaS automation.
      </div>
    </div>
  );
}
