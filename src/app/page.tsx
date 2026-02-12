import Link from 'next/link';
import { motion } from 'framer-motion';
import { BarChart, Zap, TrendingUp } from 'lucide-react';

export default function LandingPage() {
  return (
    <section className="w-full flex flex-col items-center justify-center py-24">
      <div className="max-w-5xl w-full px-8">
        <motion.h1
          className="text-5xl font-bold text-cyan-400 mb-8 font-intertight"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7 }}
        >
          KIKI Agent™: Agency-in-a-Box OaaS Platform
        </motion.h1>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          <motion.div
            className="bg-zinc-900 border border-zinc-800 rounded-xl p-8 shadow-lg flex flex-col items-center"
            whileHover={{ scale: 1.04, boxShadow: '0 0 16px 2px #22d3ee' }}
          >
            <BarChart className="w-8 h-8 text-cyan-400 mb-2" />
            <span className="text-2xl font-bold text-cyan-400 mb-2">Campaign Optimization</span>
            <p className="text-zinc-300 mb-4">Cross-platform bid orchestration and performance maximization.</p>
            <Link href="/services/campaign-optimization" className="bg-cyan-400 text-zinc-950 font-bold px-6 py-2 rounded-lg shadow hover:bg-cyan-300 transition">Deep Dive</Link>
          </motion.div>
          <motion.div
            className="bg-zinc-900 border border-zinc-800 rounded-xl p-8 shadow-lg flex flex-col items-center"
            whileHover={{ scale: 1.04, boxShadow: '0 0 16px 2px #22d3ee' }}
          >
            <TrendingUp className="w-8 h-8 text-cyan-400 mb-2" />
            <span className="text-2xl font-bold text-cyan-400 mb-2">Predictive Growth</span>
            <p className="text-zinc-300 mb-4">LTV prediction and churn forecasting for sustainable growth.</p>
            <Link href="/services/predictive-growth" className="bg-cyan-400 text-zinc-950 font-bold px-6 py-2 rounded-lg shadow hover:bg-cyan-300 transition">Deep Dive</Link>
          </motion.div>
          <motion.div
            className="bg-zinc-900 border border-zinc-800 rounded-xl p-8 shadow-lg flex flex-col items-center"
            whileHover={{ scale: 1.04, boxShadow: '0 0 16px 2px #22d3ee' }}
          >
            <Zap className="w-8 h-8 text-cyan-400 mb-2" />
            <span className="text-2xl font-bold text-cyan-400 mb-2">Revenue Attribution</span>
            <p className="text-zinc-300 mb-4">SyncLedger™ tracks Net Profit Uplift and performance-based fee attribution.</p>
            <Link href="/services/revenue-attribution" className="bg-cyan-400 text-zinc-950 font-bold px-6 py-2 rounded-lg shadow hover:bg-cyan-300 transition">Deep Dive</Link>
          </motion.div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          <motion.div className="bg-zinc-900 border border-zinc-800 rounded-xl p-8 shadow-lg flex flex-col items-center" whileHover={{ scale: 1.04 }}>
            <span className="text-2xl font-bold text-cyan-400 mb-2">Integrations</span>
            <p className="text-zinc-300 mb-4">Connect TikTok, Meta, Salesforce, PayPal.</p>
            <Link href="/integrations" className="bg-cyan-400 text-zinc-950 font-bold px-6 py-2 rounded-lg shadow hover:bg-cyan-300 transition">View Integrations</Link>
          </motion.div>
          <motion.div className="bg-zinc-900 border border-zinc-800 rounded-xl p-8 shadow-lg flex flex-col items-center" whileHover={{ scale: 1.04 }}>
            <span className="text-2xl font-bold text-cyan-400 mb-2">Docs</span>
            <p className="text-zinc-300 mb-4">Technical documentation for the OaaS model.</p>
            <Link href="/docs" className="bg-cyan-400 text-zinc-950 font-bold px-6 py-2 rounded-lg shadow hover:bg-cyan-300 transition">View Docs</Link>
          </motion.div>
          <motion.div className="bg-zinc-900 border border-zinc-800 rounded-xl p-8 shadow-lg flex flex-col items-center" whileHover={{ scale: 1.04 }}>
            <span className="text-2xl font-bold text-cyan-400 mb-2">API Reference</span>
            <p className="text-zinc-300 mb-4">Swagger-style REST API for KikiAgent™ endpoints.</p>
            <Link href="/api" className="bg-cyan-400 text-zinc-950 font-bold px-6 py-2 rounded-lg shadow hover:bg-cyan-300 transition">API Reference</Link>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
