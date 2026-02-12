import { NetProfitUplift } from '../types';
import { useState, useEffect } from 'react';
import { SyncTwinGate } from './components/SyncTwinGate';
import { ExplainabilityFeed } from './components/ExplainabilityFeed';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export default function DashboardPage() {
  const [uplift, setUplift] = useState<NetProfitUplift | null>(null);

  useEffect(() => {
    // Mock fetch for Net Profit Uplift
    setTimeout(() => {
      setUplift({
        baselineRevenue: 120000,
        newRevenue: 145000,
        baselineAdSpend: 40000,
        newAdSpend: 42000,
        netProfitUplift: 23000,
        kikiFee: 4600,
      });
    }, 1000);
  }, []);

  return (
    <div className="flex flex-col gap-8">
      <section className="bg-zinc-800 rounded-xl p-8 shadow-lg">
        <h2 className="text-2xl font-bold mb-4">Net Profit Uplift</h2>
        {uplift ? (
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={[uplift]}>
              <XAxis dataKey="baselineRevenue" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="netProfitUplift" stroke="#38bdf8" strokeWidth={3} />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="animate-pulse h-32 bg-zinc-700 rounded" />
        )}
      </section>
      <SyncTwinGate />
      <ExplainabilityFeed />
    </div>
  );
}
