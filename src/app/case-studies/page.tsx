import React from 'react';
import { motion } from 'framer-motion';
import { ShieldCheck, FileText } from 'lucide-react';

const caseStudies = [
  {
    title: 'E-Commerce Brand: $1.2M Net Profit Uplift',
    summary: 'KIKI Agent™ orchestrated cross-platform campaigns, resulting in a 28% increase in LTV and a $1.2M net profit uplift. All results independently verified by SyncLedger™.',
    compliance: 'SOC2 Type II, GDPR, ISO 27001',
  },
  {
    title: 'Fintech SaaS: 20% Churn Reduction',
    summary: 'Predictive Growth and CRM automation cut churn by 20%, with all customer data encrypted and audit-logged by SyncShield™.',
    compliance: 'SOC2 Type II, GDPR',
  },
];

export default function CaseStudiesPage() {
  return (
    <section className="max-w-5xl mx-auto py-12 px-6">
      <motion.h1
        className="text-3xl font-bold text-cyan-400 mb-4"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7 }}
      >
        Case Studies & Compliance
      </motion.h1>
      <p className="text-zinc-400 mb-8">Real-world OaaS outcomes, verified by SyncLedger™ and protected by SyncShield™ compliance.</p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {caseStudies.map(({ title, summary, compliance }) => (
          <motion.div
            key={title}
            className="bg-zinc-900 border border-zinc-800 rounded-xl p-8 shadow-lg flex flex-col gap-4"
            whileHover={{ scale: 1.03, boxShadow: '0 0 12px 2px #22d3ee' }}
          >
            <FileText className="w-7 h-7 text-cyan-400 mb-2" />
            <div className="text-xl font-bold text-white mb-1">{title}</div>
            <div className="text-zinc-300 mb-2">{summary}</div>
            <div className="flex items-center gap-2 text-zinc-400 text-sm mt-2">
              <ShieldCheck className="w-5 h-5 text-cyan-400" />
              <span>Compliance: {compliance}</span>
            </div>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
