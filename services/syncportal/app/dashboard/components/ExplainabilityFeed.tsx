import { ExplainabilityLog } from '../../types';
import { useEffect, useState } from 'react';

const mockLogs: ExplainabilityLog[] = [
  { agent: 'SyncBrain', timestamp: '2026-02-08T09:00:00Z', message: 'Strategy generated for new campaign.' },
  { agent: 'SyncTwin', timestamp: '2026-02-08T09:01:00Z', message: 'Simulation completed. ConfidenceScore: 0.92.' },
  { agent: 'SyncFlow', timestamp: '2026-02-08T09:02:00Z', message: 'Bid submitted for high-LTV user.' },
  { agent: 'SyncShield', timestamp: '2026-02-08T09:03:00Z', message: 'Risk scan passed. Creative approved.' },
];

export function ExplainabilityFeed() {
  const [logs, setLogs] = useState<ExplainabilityLog[]>([]);

  useEffect(() => {
    // Mock fetch logs
    setTimeout(() => setLogs(mockLogs), 800);
  }, []);

  return (
    <section className="bg-zinc-800 rounded-xl p-6 mt-8 shadow-lg">
      <h3 className="text-xl font-semibold mb-4">Explainability Feed</h3>
      <div className="flex flex-col gap-2 max-h-64 overflow-y-auto">
        {logs.length === 0 ? (
          <div className="animate-pulse h-16 bg-zinc-700 rounded" />
        ) : (
          logs.map((log, idx) => (
            <div key={idx} className="border-l-4 border-blue-400 pl-4 py-2">
              <span className="font-bold text-blue-300">[{log.agent}]</span> <span className="text-xs text-slate-400">{log.timestamp}</span>
              <div className="mt-1">{log.message}</div>
            </div>
          ))
        )}
      </div>
    </section>
  );
}
