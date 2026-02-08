import { LucideBarChart3, LucideShield, LucideBrain, LucideCheckCircle2 } from 'lucide-react';

export function SummaryStats() {
  // Example stats, replace with real API data
  const stats = [
    { label: 'Net Profit Uplift', value: '$42,500', icon: LucideBarChart3 },
    { label: 'Simulation Confidence', value: '0.92', icon: LucideBrain },
    { label: 'Compliance Events', value: '0', icon: LucideShield },
    { label: 'Approved Strategies', value: '7', icon: LucideCheckCircle2 },
  ];
  return (
    <div className="flex flex-wrap gap-6 justify-center md:justify-start">
      {stats.map(({ label, value, icon: Icon }) => (
        <div key={label} className="bg-zinc-900 rounded-xl px-6 py-4 flex items-center gap-4 shadow-lg border border-zinc-800">
          <Icon className="w-7 h-7 text-sky-400" />
          <div>
            <div className="text-lg font-semibold">{value}</div>
            <div className="text-xs text-zinc-400 uppercase tracking-wide">{label}</div>
          </div>
        </div>
      ))}
    </div>
  );
}
