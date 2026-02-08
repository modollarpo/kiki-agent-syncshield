import { SyncTwinSimulation } from '../../types';
import { useState } from 'react';
import { motion } from 'framer-motion';

export function SyncTwinGate() {
  const [sim, setSim] = useState<SyncTwinSimulation | null>(null);
  const [decision, setDecision] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSimulate = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/synctwin/simulate', { method: 'POST' });
      const data = await response.json();
      setSim(data);
    } finally {
      setLoading(false);
    }
  };

  const handleApprove = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/synctwin/approve', { method: 'POST' });
      const data = await response.json();
      setDecision(data.status);
    } finally {
      setLoading(false);
    }
  };

  const handleReject = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/synctwin/reject', { method: 'POST' });
      const data = await response.json();
      setDecision(data.status);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="bg-zinc-800 rounded-xl p-6 mt-8 shadow-lg flex flex-col gap-4">
      <h3 className="text-xl font-semibold">SyncTwin™ Simulation Gate</h3>
      <button className="bg-blue-500 text-white px-4 py-2 rounded" onClick={handleSimulate} disabled={loading}>
        {loading ? 'Running...' : 'Run Simulation'}
      </button>
      {sim && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mt-4">
          <div>Confidence Score: <span className="font-bold">{sim.confidenceScore}</span></div>
          <div>Risk Profile: <span className="font-bold">{sim.riskProfile}</span></div>
          <div>Projected Net Profit Uplift: <span className="font-bold">${sim.projectedNetProfitUplift}</span></div>
          <div className="flex gap-4 mt-4">
            <button className="bg-green-600 px-4 py-2 rounded text-white" onClick={handleApprove} disabled={loading}>Approve</button>
            <button className="bg-red-600 px-4 py-2 rounded text-white" onClick={handleReject} disabled={loading}>Reject</button>
          </div>
          {decision && (
            <div className="mt-2 text-lg font-semibold">Decision: {decision}</div>
          )}
        </motion.div>
      )}
    </section>
  );
}
