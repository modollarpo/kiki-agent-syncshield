import React from 'react';

export default function PredictiveGrowthPage() {
  return (
    <section className="max-w-4xl mx-auto py-12 px-6">
      <h1 className="text-3xl font-bold text-cyan-400 mb-4">Predictive Growth</h1>
      <p className="text-zinc-400 mb-8">Explore KIKI's LTV prediction and churn forecasting engine for sustainable growth.</p>
      <button className="mt-8 bg-white text-black font-bold px-5 py-2 rounded shadow-md hover:bg-cyan-400 hover:text-zinc-950 transition" onClick={() => window.location.href='/onboarding'}>
        Get Started
      </button>
    </section>
  );
}
