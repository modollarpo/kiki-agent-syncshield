"use client";
"use client";
import { useEffect, useState } from "react";

type KPI = {
  metric: string;
  ai_agent: string | number;
  manual_baseline: string | number;
  revenue_win: string | number;
};

export default function AIVsManualKPIWidget() {
  const [kpis, setKpis] = useState<KPI[]>([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    fetch("/dashboard/ai-vs-manual-kpis")
      .then((res) => res.json())
      .then((data) => setKpis(data.kpis || []))
      .finally(() => setLoading(false));
  }, []);
  return (
    <div className="rounded-xl p-4 bg-slate-900/50 border border-slate-800 mb-8">
      <div className="font-semibold mb-2">AI vs. Manual Performance</div>
      <table className="min-w-full text-xs">
        <thead>
          <tr className="text-zinc-400">
            <th className="px-2 py-1 text-left">Metric</th>
            <th className="px-2 py-1 text-left">AI Agent</th>
            <th className="px-2 py-1 text-left">Manual Baseline</th>
            <th className="px-2 py-1 text-left">Revenue Win</th>
          </tr>
        </thead>
        <tbody>
          {loading && (
            <tr><td colSpan={4} className="text-zinc-400 px-2 py-1">Loading...</td></tr>
          )}
          {kpis.map((row, i) => (
            <tr key={i}>
              <td className="px-2 py-1 whitespace-nowrap font-semibold">{row.metric}</td>
              <td className="px-2 py-1">{row.ai_agent}</td>
              <td className="px-2 py-1">{row.manual_baseline}</td>
              <td className="px-2 py-1 text-emerald-400">{row.revenue_win}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
