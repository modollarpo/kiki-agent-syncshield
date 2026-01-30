"use client";
import React, { useState } from "react";
import { sendAttribution, getPerformance } from "./api";

export const AttributionWidget: React.FC = () => {
  const [creativeId, setCreativeId] = useState("");
  const [ctr, setCtr] = useState(0.0);
  const [conversions, setConversions] = useState(0);
  const [platform, setPlatform] = useState("instagram");
  const [style, setStyle] = useState("");
  const [result, setResult] = useState<any>(null);
  const [perf, setPerf] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    setLoading(true);
    const res = await sendAttribution(creativeId, ctr, conversions, platform, style);
    setResult(res);
    setLoading(false);
  };

  const handleGetPerf = async () => {
    setLoading(true);
    const data = await getPerformance(creativeId);
    setPerf(data);
    setLoading(false);
  };

  return (
    <div className="p-4 rounded bg-slate-900/50 border border-slate-800 mb-8">
      <div className="font-semibold mb-2">Attribution Feedback</div>
      <div className="flex gap-2 mb-2">
        <input className="p-2 rounded bg-slate-800 text-white" placeholder="Creative ID" value={creativeId} onChange={e => setCreativeId(e.target.value)} />
        <input type="number" step="0.001" className="p-2 rounded bg-slate-800 text-white" placeholder="CTR" value={ctr} onChange={e => setCtr(Number(e.target.value))} />
        <input type="number" className="p-2 rounded bg-slate-800 text-white" placeholder="Conversions" value={conversions} onChange={e => setConversions(Number(e.target.value))} />
        <select value={platform} onChange={e => setPlatform(e.target.value)} className="p-2 rounded bg-slate-800 text-white">
          <option value="instagram">Instagram</option>
          <option value="linkedin">LinkedIn</option>
          <option value="youtube">YouTube</option>
        </select>
        <input className="p-2 rounded bg-slate-800 text-white" placeholder="Style" value={style} onChange={e => setStyle(e.target.value)} />
        <button onClick={handleSend} className="bg-emerald-600 px-4 py-2 rounded text-white font-semibold" disabled={loading}>Send Attribution</button>
        <button onClick={handleGetPerf} className="bg-blue-600 px-4 py-2 rounded text-white font-semibold" disabled={loading}>Get Performance</button>
      </div>
      {result && (
        <div className="mt-2 text-xs text-zinc-400">Action: {result.action} for {result.creative_id}</div>
      )}
      {perf && (
        <div className="mt-2 text-xs text-emerald-400">Performance: CTR={perf.ctr}, Conversions={perf.conversions}, Platform={perf.platform}, Style={perf.style}</div>
      )}
    </div>
  );
};
