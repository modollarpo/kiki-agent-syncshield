import Link from 'next/link';
import { motion } from 'framer-motion';

export default function CampaignOptimization() {
  return (
    <div className="min-h-screen bg-zinc-950 text-white flex flex-col items-center justify-center">
      <motion.div
        initial={{ opacity: 0, y: -40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7 }}
        className="w-full max-w-3xl px-8 py-16 text-center"
      >
        <h1 className="font-calsans text-5xl font-bold mb-6 text-cyan-400">
          Sub-Second Bidding. Creative Rotation. Unstoppable Profit.
        </h1>
        <svg width="120" height="120" className="mx-auto mb-8" viewBox="0 0 120 120" fill="none">
          <motion.path
            d="M10 60 Q60 10 110 60 Q60 110 10 60"
            stroke="#38bdf8"
            strokeWidth="2"
            fill="none"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 1.2 }}
          />
        </svg>
        <p className="text-lg font-intertight mb-8">
          KIKI Agent™ analyzes 1,440 micro-signals a day to move your budget to the highest-yielding creative. Every dollar is algorithmically allocated for maximum Net Profit Uplift. No wasted spend. No manual guesswork. Just autonomous optimization.
        </p>
        <div className="bg-zinc-900 rounded-xl p-6 mb-8 shadow-lg border border-zinc-800">
          <h2 className="font-calsans text-2xl text-cyan-400 mb-2">How It Works</h2>
          <ul className="text-left text-base font-intertight list-disc list-inside mb-4">
            <li>Real-time API integration with Meta, Google, TikTok, LinkedIn, Amazon, Microsoft</li>
            <li>SyncTwin™ runs 10,000 pre-launch simulations to block unprofitable campaigns</li>
            <li>SyncFlow™ executes sub-second bids, shifting capital to top-performing creatives</li>
            <li>MarginGuardian circuit breaker prevents overspend during market shocks</li>
          </ul>
          <div className="bg-zinc-800 rounded p-4 mt-4">
            <h3 className="font-calsans text-lg text-cyan-400 mb-2">SyncLedger™ Proof</h3>
            <p className="text-sm font-intertight">
              Every optimization event is logged in SyncLedger™. You see exactly which creative, platform, and bid drove your Net Profit Uplift. No more "black box" reporting.
            </p>
          </div>
        </div>
        <Link href="/onboarding?service=campaign-optimization">
          <button className="bg-cyan-400 text-zinc-950 font-bold px-8 py-4 rounded-xl text-xl shadow-lg hover:bg-cyan-300 transition">
            Activate Optimization Agent →
          </button>
        </Link>
      </motion.div>
      <footer className="mt-16 text-xs text-zinc-500">
        SOC2 Type II • ISO 27001 • © 2026 KIKI™ Enterprise Platform.
      </footer>
    </div>
  );
}
