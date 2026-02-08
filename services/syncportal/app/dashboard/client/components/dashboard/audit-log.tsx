import { LucideShield } from 'lucide-react';

const logs = [
  { time: '09:12', action: 'Budget reallocated: Meta → Google', by: 'SyncFlow', details: '+$1,200 to Google Ads' },
  { time: '10:03', action: 'Creative swapped', by: 'SyncCreate', details: 'Deployed Gold Standard asset' },
  { time: '11:15', action: 'Manual circuit breaker', by: 'Client', details: 'Paused TikTok campaign' },
  { time: '12:00', action: 'Audit event', by: 'SyncShield', details: 'All actions logged (SOC2/GDPR)' },
];

export function AuditLog() {
  return (
    <div className="bg-zinc-900 rounded-xl p-6 shadow-lg border border-zinc-800">
      <div className="flex items-center gap-2 mb-2">
        <LucideShield className="w-5 h-5 text-sky-400" />
        <h2 className="text-lg font-bold">Sovereign Audit Log</h2>
      </div>
      <div className="space-y-3 max-h-64 overflow-y-auto">
        {logs.map((log, i) => (
          <div key={i} className="flex flex-col border-b border-zinc-800 pb-2 last:border-b-0">
            <div className="flex gap-2 items-center text-sm">
              <span className="text-zinc-400">{log.time}</span>
              <span className="font-semibold text-zinc-200">{log.action}</span>
              <span className="ml-auto text-xs text-zinc-500">by {log.by}</span>
            </div>
            <div className="text-xs text-zinc-400 pl-8">{log.details}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
