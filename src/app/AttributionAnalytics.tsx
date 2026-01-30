"use client";
import React, { useState } from "react";
import { getPerformance } from "./api";
import { AttributionTrendChart } from "./AttributionTrendChart";

export const AttributionAnalytics: React.FC = () => {
  const [creativeId, setCreativeId] = useState("");
  const [perf, setPerf] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<any[]>([]);

  const handleGetPerf = async () => {
    setLoading(true);
    const data = await getPerformance(creativeId);
    setPerf(data);
    setHistory(h => [...h, { ...data, timestamp: new Date().toLocaleString() }]);
    setLoading(false);
  };

  return (
    <div className="p-4 rounded bg-slate-900/50 border border-slate-800 mb-8">
      <div className="font-semibold mb-2">Attribution Analytics</div>
      <div className="flex gap-2 mb-2">
        <input className="p-2 rounded bg-slate-800 text-white" placeholder="Creative ID" value={creativeId} onChange={e => setCreativeId(e.target.value)} />
        <button onClick={handleGetPerf} className="bg-blue-600 px-4 py-2 rounded text-white font-semibold" disabled={loading}>Get Performance</button>
      </div>
      {perf && (
        <div className="mt-2 text-xs text-emerald-400">Current: CTR={perf.ctr}, Conversions={perf.conversions}, Platform={perf.platform}, Style={perf.style}</div>
      )}
      {history.length > 0 && (
        <div className="mt-4">
          <div className="font-semibold mb-1">Performance History</div>
          <AttributionTrendChart history={history} />
          <table className="min-w-full text-xs mt-4">
            <thead>
              <tr className="text-zinc-400">
                <th className="px-2 py-1 text-left">Time</th>
                <th className="px-2 py-1 text-left">CTR</th>
                <th className="px-2 py-1 text-left">Conversions</th>
                <th className="px-2 py-1 text-left">Platform</th>
                <th className="px-2 py-1 text-left">Style</th>
              </tr>
            </thead>
            <tbody>
              {history.map((h, i) => (
                <tr key={i}>
                  <td className="px-2 py-1 whitespace-nowrap">{h.timestamp}</td>
                  <td className="px-2 py-1">{h.ctr}</td>
                  <td className="px-2 py-1">{h.conversions}</td>
                  <td className="px-2 py-1">{h.platform}</td>
                  <td className="px-2 py-1">{h.style}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
