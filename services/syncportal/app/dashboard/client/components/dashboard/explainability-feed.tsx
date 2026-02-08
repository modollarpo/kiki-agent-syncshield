import { LucideSparkles } from 'lucide-react';

const explainabilityEvents = [
  {
    time: '09:15',
    message: 'SyncFlow shifted 15% budget to Google Ads due to 22% higher LTV signals.',
  },
  {
    time: '10:10',
    message: 'SyncTwin simulation flagged TikTok campaign for underperformance (Confidence: 0.78).',
  },
  {
    time: '10:45',
    message: 'SyncShield auto-paused Meta campaign after policy violation detected.',
  },
  {
    time: '11:30',
    message: 'Explainability Broker: "AI prioritized high-LTV segments over click volume."',
  },
];

export function ExplainabilityFeed() {
  return (
    <div className="bg-zinc-900 rounded-xl p-6 shadow-lg border border-zinc-800">
      <div className="flex items-center gap-2 mb-2">
        <LucideSparkles className="w-5 h-5 text-sky-400" />
        <h2 className="text-lg font-bold">Explainability Feed</h2>
      </div>
      <div className="space-y-3 max-h-64 overflow-y-auto">
        {explainabilityEvents.map((event, i) => (
          <div key={i} className="flex gap-2 items-center text-sm border-b border-zinc-800 pb-2 last:border-b-0">
            <span className="text-zinc-400">{event.time}</span>
            <span className="text-zinc-200">{event.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
