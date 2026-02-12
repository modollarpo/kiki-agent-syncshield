import React from 'react';
import { motion } from 'framer-motion';
import { Cloud, Facebook, CreditCard, Music } from 'lucide-react';

const integrations = [
  { name: 'TikTok', icon: <Music className="w-8 h-8 text-cyan-400" /> },
  { name: 'Meta', icon: <Facebook className="w-8 h-8 text-blue-500" /> },
  { name: 'Salesforce', icon: <Cloud className="w-8 h-8 text-blue-400" /> },
  { name: 'PayPal', icon: <CreditCard className="w-8 h-8 text-yellow-400" /> },
];

export default function IntegrationsPage() {
  return (
    <section className="max-w-4xl mx-auto py-12 px-6">
      <motion.h1
        className="text-3xl font-bold text-cyan-400 mb-4"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7 }}
      >
        Seamless Integration Ecosystem
      </motion.h1>
      <p className="text-zinc-400 mb-8">Connect your ad platforms and CRM for full OaaS automation.</p>
      <div className="grid grid-cols-2 gap-8 mt-8">
        {integrations.map(({ name, icon }) => (
          <motion.div
            key={name}
            className="flex items-center gap-4 border border-zinc-800 rounded-lg p-6 bg-zinc-900"
            whileHover={{ scale: 1.05, boxShadow: '0 0 12px 2px #22d3ee' }}
          >
            {icon}
            <span className="text-lg font-semibold text-white">{name}</span>
          </motion.div>
        ))}
      </div>
    </section>
  );
}
