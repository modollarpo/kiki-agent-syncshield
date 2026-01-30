"use client";
import React, { useState } from "react";
import { sendAttribution } from "./api";

export const CreativeOptimizer: React.FC = () => {
  const [creativeId, setCreativeId] = useState("");
  const [ctr, setCtr] = useState(0.0);
  const [conversions, setConversions] = useState(0);
  const [platform, setPlatform] = useState("instagram");
  const [style, setStyle] = useState("");
  const [triggered, setTriggered] = useState(false);
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);

  const handleOptimize = async () => {
    setLoading(true);
    const res = await sendAttribution(creativeId, ctr, conversions, platform, style);
    if (res.action === "negative_weight") {
      setMessage(`Creative ${creativeId} flagged for optimization. PromptEngineer will pivot style.`);
      setTriggered(true);
    } else {
      setMessage(`Creative ${creativeId} is performing well. No action needed.`);
      setTriggered(false);
    }
    setLoading(false);
  };

  return (
    <div className="p-4 rounded bg-slate-900/50 border border-slate-800 mb-8">
      <div className="font-semibold mb-2">Automated Creative Optimization Trigger</div>
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
        <button onClick={handleOptimize} className="bg-emerald-600 px-4 py-2 rounded text-white font-semibold" disabled={loading}>Trigger Optimization</button>
      </div>
      {message && (
        <div className={`mt-2 text-xs ${triggered ? "text-orange-400" : "text-emerald-400"}`}>{message}</div>
      )}
    </div>
  );
};
