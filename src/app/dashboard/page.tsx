import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { BarChart, DollarSign } from 'lucide-react';

import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

export default function DashboardPage() {
  const [form, setForm] = useState({ monthly_customers: 1000, ltv: 450, churn: 8 });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [history, setHistory] = useState([]);
  // SyncTwin simulation state
  const [simInput, setSimInput] = useState({ strategy: 'acquire_high_ltv', budget: 10000 });
  const [simResult, setSimResult] = useState(null);
  const [simLoading, setSimLoading] = useState(false);
  const [simError, setSimError] = useState('');

  // SyncTwin simulation handler
  const handleSimChange = (e) => {
    setSimInput({ ...simInput, [e.target.name]: e.target.value });
  };
  const handleSimSubmit = async (e) => {
    e.preventDefault();
    setSimLoading(true);
    setSimError('');
    setSimResult(null);
    try {
      const res = await fetch('/simulate_strategy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          strategy: simInput.strategy,
          budget: Number(simInput.budget),
        }),
      });
      if (!res.ok) {
        let msg = 'SyncTwin error';
        try {
          const errData = await res.json();
          msg = errData.detail || msg;
        } catch {}
        throw new Error(msg);
      }
      const data = await res.json();
      setSimResult(data);
    } catch (err) {
      setSimError(err?.message || 'Failed to simulate strategy.');
    } finally {
      setSimLoading(false);
    }
  };

  useEffect(() => {
    async function fetchHistory() {
      try {
        const res = await fetch('/audit_log');
        if (!res.ok) return;
        const data = await res.json();
        // Assume audit log is an array of events, filter for impact_audit_response
        const events = Array.isArray(data) ? data : (data?.events || []);
        const impactEvents = events.filter(e => e.event_type === 'impact_audit_response');
        // Parse and map to chart data
        const chartData = impactEvents.slice(-10).map((e, i) => {
          const p = e.payload || e;
          return {
            name: `#${i + 1}`,
            uplift: Number(p.projected_uplift) || 0,
            fee: Number(p.kiki_performance_fee) || 0,
          };
        });
        setHistory(chartData);
      } catch {}
    }
    fetchHistory();
  }, [result]);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const res = await fetch('/impact_audit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          monthly_customers: Number(form.monthly_customers),
          ltv: Number(form.ltv),
          churn: Number(form.churn),
        }),
      });
      if (!res.ok) {
        let msg = 'API error';
        try {
          const errData = await res.json();
          msg = errData.detail || msg;
        } catch {}
        setResult(null);
        throw new Error(msg);
      }
      const data = await res.json();
      setResult(data);
    } catch (err) {
      setResult(null);
      setError(err?.message || 'Failed to fetch uplift data.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="max-w-5xl mx-auto py-12 px-6">
      <motion.h1
        className="text-4xl font-bold text-cyan-400 mb-6"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7 }}
      >
        Sovereign Dashboard
      </motion.h1>
      <form onSubmit={handleSubmit} className="mb-10 bg-zinc-900 border border-zinc-800 rounded-xl p-8 flex flex-col md:flex-row gap-6 items-end">
        <div>
          <label className="block text-zinc-400 mb-1">Monthly Customers</label>
          <input type="number" name="monthly_customers" value={form.monthly_customers} onChange={handleChange} className="bg-zinc-800 text-white rounded px-3 py-2 w-32" min={0} required />
        </div>
        <div>
          <label className="block text-zinc-400 mb-1">Average LTV ($)</label>
          <input type="number" name="ltv" value={form.ltv} onChange={handleChange} className="bg-zinc-800 text-white rounded px-3 py-2 w-32" min={0} required />
        </div>
        <div>
          <label className="block text-zinc-400 mb-1">Churn Rate (%)</label>
          <input type="number" name="churn" value={form.churn} onChange={handleChange} className="bg-zinc-800 text-white rounded px-3 py-2 w-32" min={0} max={100} required />
        </div>
        <button type="submit" className="bg-cyan-400 text-zinc-950 font-bold px-6 py-2 rounded-lg shadow hover:bg-cyan-300 transition" disabled={loading}>
          {loading ? 'Calculating...' : 'Calculate Uplift'}
        </button>
      </form>
      {error && <div className="text-red-400 mb-4">{error}</div>}
      {result && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
            <motion.div className="bg-zinc-900 border border-zinc-800 rounded-xl p-8 shadow-lg" whileHover={{ scale: 1.03 }}>
              <BarChart className="w-8 h-8 text-cyan-400 mb-2" />
              <div className="text-xl font-bold text-cyan-400 mb-2">Net Profit Uplift</div>
              <div className="text-3xl font-bold text-white mb-2">${result.projected_uplift.toLocaleString()}</div>
              <div className="text-zinc-400 text-sm">(New Revenue - Baseline Revenue) - (New Ad Spend - Baseline Ad Spend)</div>
            </motion.div>
            <motion.div className="bg-zinc-900 border border-zinc-800 rounded-xl p-8 shadow-lg" whileHover={{ scale: 1.03 }}>
              <DollarSign className="w-8 h-8 text-cyan-400 mb-2" />
              <div className="text-xl font-bold text-cyan-400 mb-2">KIKI Success Fee (20%)</div>
              <div className="text-3xl font-bold text-white mb-2">${result.kiki_performance_fee.toLocaleString()}</div>
              <div className="text-zinc-400 text-sm">Only charged if Net Profit Uplift is positive</div>
            </motion.div>
          </div>
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-8 shadow-lg mb-8">
            <div className="text-lg font-bold text-cyan-400 mb-2">Uplift Scenarios</div>
            <div className="flex flex-col md:flex-row gap-8">
              <div>
                <div className="text-zinc-400">Conservative Uplift</div>
                <div className="text-white text-xl">${result.conservative_uplift.toLocaleString()}</div>
                <div className="text-zinc-400 mt-2">Aggressive Uplift</div>
                <div className="text-white text-xl">${result.aggressive_uplift.toLocaleString()}</div>
              </div>
              <div>
                <div className="text-zinc-400">Client Net Profit</div>
                <div className="text-white text-xl">${result.client_net_profit.toLocaleString()}</div>
                <div className="text-zinc-400 mt-2">Prospect ID</div>
                <div className="text-white text-xl">{result.prospect_id}</div>
              </div>
            </div>
          </div>
          {history.length > 0 && (
            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-8 shadow-lg mb-8">
              <div className="text-lg font-bold text-cyan-400 mb-4">Recent Net Profit Uplift (Last 10)</div>
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={history} margin={{ left: 8, right: 8, top: 8, bottom: 8 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#222" />
                  <XAxis dataKey="name" stroke="#888" />
                  <YAxis stroke="#888" />
                  <Tooltip />
                  <Line type="monotone" dataKey="uplift" stroke="#22d3ee" strokeWidth={3} dot={false} name="Net Profit Uplift" />
                  <Line type="monotone" dataKey="fee" stroke="#fbbf24" strokeWidth={2} dot={false} name="KIKI Fee" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}
        </>
      )}
      {/* SyncTwin Simulation Section */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-8 shadow-lg mb-8 mt-8">
        <div className="text-lg font-bold text-cyan-400 mb-4">SyncTwin™ Pre-Launch Simulation</div>
        <form onSubmit={handleSimSubmit} className="flex flex-col md:flex-row gap-6 items-end mb-4">
          <div>
            <label className="block text-zinc-400 mb-1">Strategy</label>
            <input type="text" name="strategy" value={simInput.strategy} onChange={handleSimChange} className="bg-zinc-800 text-white rounded px-3 py-2 w-48" required />
          </div>
          <div>
            <label className="block text-zinc-400 mb-1">Budget ($)</label>
            <input type="number" name="budget" value={simInput.budget} onChange={handleSimChange} className="bg-zinc-800 text-white rounded px-3 py-2 w-32" min={0} required />
          </div>
          <button type="submit" className="bg-cyan-400 text-zinc-950 font-bold px-6 py-2 rounded-lg shadow hover:bg-cyan-300 transition" disabled={simLoading}>
            {simLoading ? 'Simulating...' : 'Simulate'}
          </button>
        </form>
        {simError && <div className="text-red-400 mb-4">{simError}</div>}
        {simResult && (
          <div className="mt-4">
            <div className="text-cyan-400 font-bold mb-2">Simulation Result</div>
            <div className="text-white text-sm whitespace-pre-wrap bg-zinc-800 rounded p-4">
              {JSON.stringify(simResult, null, 2)}
            </div>
          </div>
        )}
      </div>
      <div className="text-zinc-400 text-sm mt-8">Powered by SyncLedger™ | Real-time OaaS Attribution</div>
    </section>
  );
}