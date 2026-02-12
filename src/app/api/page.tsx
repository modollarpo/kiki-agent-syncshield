import React from 'react';
import dynamic from 'next/dynamic';
import { motion } from 'framer-motion';

// Dynamically import SwaggerUI to avoid SSR issues
const SwaggerUI = dynamic(() => import('swagger-ui-react'), { ssr: false });
import 'swagger-ui-react/swagger-ui.css';

export default function APIPage() {
  return (
    <section className="max-w-5xl mx-auto py-12 px-6">
      <motion.h1
        className="text-3xl font-bold text-cyan-400 mb-4"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7 }}
      >
        KIKI Agent™ API Reference
      </motion.h1>
      <p className="text-zinc-400 mb-8">Explore the interactive REST API documentation for the KIKI OaaS platform. Try endpoints live below.</p>
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
        <SwaggerUI url="/openapi/openapi.yaml" />
      </div>
    </section>
  );
}
