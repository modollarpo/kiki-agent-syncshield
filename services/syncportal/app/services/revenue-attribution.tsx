import Link from 'next/link';
import { motion } from 'framer-motion';

export default function RevenueAttribution() {
  return (
    <div className="min-h-screen bg-zinc-950 text-white flex flex-col items-center justify-center">
      <motion.div
        initial={{ opacity: 0, y: -40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7 }}
        className="w-full max-w-3xl px-8 py-16 text-center"
      >
        <h1 className="font-calsans text-5xl font-bold mb-6 text-cyan-400">
          SyncLedger™: The Source of Truth for Revenue.
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
          KIKI Agent™ reconciles Shopify, Stripe, and Ad API data in real-time. Every dollar is tracked, every attribution is transparent. No more "platform guesswork"—just verifiable profit uplift, logged and auditable.
        </p>
        <div className="bg-zinc-900 rounded-xl p-6 mb-8 shadow-lg border border-zinc-800">
          <h2 className="font-calsans text-2xl text-cyan-400 mb-2">How It Works</h2>
          <ul className="text-left text-base font-intertight list-disc list-inside mb-4">
            <li>SyncLedger™ connects to Shopify, Stripe, WooCommerce, and all major Ad APIs</li>
            <li>Every transaction is matched to the exact campaign, creative, and platform</li>
            <li>Immutable audit trail for compliance (SOC2, ISO 27001)</li>
            <li>Real-time Net Profit Uplift calculation—no more "last-click" attribution</li>
          </ul>
          <div className="bg-zinc-800 rounded p-4 mt-4">
            <h3 className="font-calsans text-lg text-cyan-400 mb-2">Proof of Value</h3>
            <p className="text-sm font-intertight">
              See your true profit, not just "reported revenue." SyncLedger™ exposes every dollar earned, every dollar spent, and every agent action that drove it.
            </p>
          </div>
        </div>
        <Link href="/onboarding?service=revenue-attribution">
          <button className="bg-cyan-400 text-zinc-950 font-bold px-8 py-4 rounded-xl text-xl shadow-lg hover:bg-cyan-300 transition">
            Verify Your Revenue →
          </button>
        </Link>
      </motion.div>
      <footer className="mt-16 text-xs text-zinc-500">
        SOC2 Type II • ISO 27001 • © 2026 KIKI™ Enterprise Platform.
      </footer>
    </div>
  );
}
