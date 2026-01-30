"use client";
import React, { useState } from "react";
import { runBidSimulation } from "./api";

export const RevenueSimulationTab: React.FC = () => {
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [bidAmount, setBidAmount] = useState(100);
  const [impressions, setImpressions] = useState(10000);
  const [platform, setPlatform] = useState("instagram");

  const runSimulation = async () => {
    setLoading(true);
    setResult(null);
    try {
      const data = await runBidSimulation(bidAmount, impressions, platform);
      setResult(data);
    } catch (e) {
      setResult({ error: "Simulation failed" });
    }
    setLoading(false);
  };

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Revenue Simulation</h2>
      <div className="flex gap-4 mb-4">
        <input type="number" value={bidAmount} onChange={e => setBidAmount(Number(e.target.value))} className="p-2 rounded bg-slate-800 text-white" placeholder="Bid Amount" />
        <input type="number" value={impressions} onChange={e => setImpressions(Number(e.target.value))} className="p-2 rounded bg-slate-800 text-white" placeholder="Impressions" />
        <select value={platform} onChange={e => setPlatform(e.target.value)} className="p-2 rounded bg-slate-800 text-white">
          <option value="instagram">Instagram</option>
          <option value="linkedin">LinkedIn</option>
          <option value="youtube">YouTube</option>
        </select>
        <button onClick={runSimulation} className="bg-emerald-600 px-4 py-2 rounded text-white font-semibold" disabled={loading}>{loading ? "Simulating..." : "Run Simulation"}</button>
      </div>
      {result && (
        <div className="mt-4">
          <div className="font-semibold">Success Rate: <span className="text-emerald-400">{(result.success_rate * 100).toFixed(2)}%</span></div>
          <div className="font-semibold">Confidence Interval: <span className="text-blue-400">[{(result.confidence_interval[0] * 100).toFixed(2)}%, {(result.confidence_interval[1] * 100).toFixed(2)}%]</span></div>
          <div className="font-semibold">Projected Revenue: <span className="text-emerald-400">${result.projected_revenue.toFixed(2)}</span></div>
        </div>
      )}
    </div>
  );
};
