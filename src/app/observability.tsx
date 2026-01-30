import React, { useEffect, useState } from "react";

export function ObservabilityMetrics() {
  const [gatewayMetrics, setGatewayMetrics] = useState("");
  const [createMetrics, setCreateMetrics] = useState("");
  const [engageMetrics, setEngageMetrics] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      fetch("http://localhost:8080/metrics").then(r => r.text()).catch(() => ""),
      fetch("http://localhost:8084/metrics").then(r => r.text()).catch(() => ""),
      fetch("http://localhost:8085/metrics").then(r => r.text()).catch(() => ""),
    ]).then(([gw, cr, en]) => {
      setGatewayMetrics(gw);
      setCreateMetrics(cr);
      setEngageMetrics(en);
      setLoading(false);
    });
  }, []);

  return (
    <div className="rounded-xl p-4 bg-slate-900/50 border border-slate-800 mb-8">
      <div className="font-semibold mb-2 flex items-center">Observability Metrics
        {loading && <span className="ml-2 text-xs text-zinc-400">Loading...</span>}
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-mono">
        <div>
          <div className="font-bold mb-1">API Gateway</div>
          <pre className="overflow-x-auto bg-slate-800 p-2 rounded h-48">{gatewayMetrics || "No data."}</pre>
        </div>
        <div>
          <div className="font-bold mb-1">SyncCreate</div>
          <pre className="overflow-x-auto bg-slate-800 p-2 rounded h-48">{createMetrics || "No data."}</pre>
        </div>
        <div>
          <div className="font-bold mb-1">SyncEngage</div>
          <pre className="overflow-x-auto bg-slate-800 p-2 rounded h-48">{engageMetrics || "No data."}</pre>
        </div>
      </div>
    </div>
  );
}
