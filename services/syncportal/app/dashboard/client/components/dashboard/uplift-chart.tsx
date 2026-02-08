import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const data = [
  { date: 'Mon', Baseline: 12000, KIKI: 14500 },
  { date: 'Tue', Baseline: 12500, KIKI: 15500 },
  { date: 'Wed', Baseline: 13000, KIKI: 16200 },
  { date: 'Thu', Baseline: 12800, KIKI: 17000 },
  { date: 'Fri', Baseline: 13500, KIKI: 18000 },
  { date: 'Sat', Baseline: 14000, KIKI: 18500 },
  { date: 'Sun', Baseline: 14200, KIKI: 19000 },
];

export function UpliftChart() {
  return (
    <div className="bg-zinc-900 rounded-xl p-6 shadow-lg border border-zinc-800">
      <h2 className="text-xl font-bold mb-2">Net Profit Uplift</h2>
      <ResponsiveContainer width="100%" height={220}>
        <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="colorKIKI" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#0f172a" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <XAxis dataKey="date" stroke="#94a3b8" />
          <YAxis stroke="#94a3b8" />
          <Tooltip contentStyle={{ background: '#18181b', border: 'none' }} />
          <Area type="monotone" dataKey="Baseline" stroke="#64748b" fill="#334155" fillOpacity={0.3} />
          <Area type="monotone" dataKey="KIKI" stroke="#38bdf8" fill="url(#colorKIKI)" />
        </AreaChart>
      </ResponsiveContainer>
      <div className="mt-4 text-zinc-400 text-xs">
        <span className="font-semibold text-sky-400">KIKI</span> performance vs. Baseline (last 7 days)
      </div>
    </div>
  );
}
