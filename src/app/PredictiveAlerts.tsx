"use client";
import React, { useState, useEffect } from "react";
import { getPerformance } from "./api";

export const PredictiveAlerts: React.FC = () => {
  const [creativeId, setCreativeId] = useState("");
  const [alert, setAlert] = useState<string>("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!creativeId) return;
    const interval = setInterval(async () => {
      setLoading(true);
      const perf = await getPerformance(creativeId);
      if (perf.ctr !== undefined && perf.conversions !== undefined) {
        if (perf.ctr < 0.01 || perf.conversions === 0) {
          setAlert(`ALERT: Creative ${creativeId} is underperforming! Consider triggering optimization.`);
        } else if (perf.ctr > 0.05 && perf.conversions > 10) {
          setAlert(`Creative ${creativeId} is outperforming. Scale up!`);
        } else {
          setAlert("");
        }
      }
      setLoading(false);
    }, 5000);
    return () => clearInterval(interval);
  }, [creativeId]);

  return (
    <div className="p-4 rounded bg-slate-900/50 border border-slate-800 mb-8">
      <div className="font-semibold mb-2">Predictive Alerts</div>
      <input className="p-2 rounded bg-slate-800 text-white mb-2" placeholder="Creative ID" value={creativeId} onChange={e => setCreativeId(e.target.value)} />
      {loading && <div className="text-xs text-zinc-400">Checking performance...</div>}
      {alert && <div className="text-xs text-orange-400 font-bold mt-2">{alert}</div>}
    </div>
  );
};
