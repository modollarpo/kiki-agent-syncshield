import React, { useState } from "react";

interface ImpactAuditResult {
  projected_uplift: number;
  kiki_performance_fee: number;
  client_net_profit: number;
  conservative_uplift: number;
  aggressive_uplift: number;
  prospect_id: string;
}

export const ImpactAuditForm: React.FC = () => {
  const [monthlyCustomers, setMonthlyCustomers] = useState(1000);
  const [ltv, setLtv] = useState(120.0);
  const [churn, setChurn] = useState(8.0);
  const [result, setResult] = useState<ImpactAuditResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch("/api/impact_audit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          monthly_customers: monthlyCustomers,
          ltv,
          churn,
        }),
      });
      if (!res.ok) throw new Error("API error");
      const data = await res.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-slate-900 p-8 rounded-xl border border-emerald-500/30 max-w-xl mx-auto">
      <h2 className="text-2xl font-bold text-white mb-4">Impact Audit</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-slate-300">Monthly Customers</label>
          <input type="number" min={1} value={monthlyCustomers} onChange={e => setMonthlyCustomers(Number(e.target.value))} className="w-full p-2 rounded bg-slate-800 text-white" />
        </div>
        <div>
          <label className="block text-slate-300">LTV ($)</label>
          <input type="number" min={1} step={0.01} value={ltv} onChange={e => setLtv(Number(e.target.value))} className="w-full p-2 rounded bg-slate-800 text-white" />
        </div>
        <div>
          <label className="block text-slate-300">Churn Rate (%)</label>
          <input type="number" min={0} max={100} step={0.1} value={churn} onChange={e => setChurn(Number(e.target.value))} className="w-full p-2 rounded bg-slate-800 text-white" />
        </div>
        <button type="submit" className="w-full py-3 bg-emerald-500 hover:bg-emerald-600 text-white font-bold rounded-lg transition-all" disabled={loading}>
          {loading ? "Calculating..." : "Run Audit"}
        </button>
      </form>
      {error && <div className="mt-4 text-red-400">{error}</div>}
      {result && (
        <div className="mt-6 bg-slate-800 p-4 rounded-lg text-slate-200">
          <div>Projected Uplift: <span className="text-emerald-400 font-bold">${result.projected_uplift.toLocaleString()}</span></div>
          <div>KIKI Performance Fee: <span className="text-emerald-400 font-bold">${result.kiki_performance_fee.toLocaleString()}</span></div>
          <div>Client Net Profit: <span className="text-emerald-400 font-bold">${result.client_net_profit.toLocaleString()}</span></div>
          <div>Conservative Uplift: <span className="text-slate-400">${result.conservative_uplift.toLocaleString()}</span></div>
          <div>Aggressive Uplift: <span className="text-slate-400">${result.aggressive_uplift.toLocaleString()}</span></div>
          <div className="text-xs text-slate-500 mt-2">Prospect ID: {result.prospect_id}</div>
        </div>
      )}
    </div>
  );
};
