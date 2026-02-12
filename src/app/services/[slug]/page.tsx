import { notFound } from 'next/navigation';

const servicesData: Record<string, { title: string; description: string }> = {
  'campaign-optimization': {
    title: 'Campaign Optimization',
    description: 'Sub-second bidding logic for maximum Net Profit Uplift.'
  },
  'predictive-growth': {
    title: 'Predictive Growth',
    description: 'SyncTwin™ simulations for future-proof scaling.'
  },
  'revenue-attribution': {
    title: 'Revenue Attribution',
    description: 'SyncLedger™ auditing for transparent performance settlement.'
  }
};

export default function ServicePage({ params }: { params: { slug: string } }) {
  const service = servicesData[params.slug];
  if (!service) return notFound();

  return (
    <div className="max-w-2xl mx-auto py-16">
      <h2 className="text-3xl font-bold text-cyan-400 mb-8 font-intertight">{service.title}</h2>
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-8 shadow-lg">
        <p className="text-zinc-300 mb-4">{service.description}</p>
        <a href="/onboarding" className="bg-cyan-400 text-zinc-950 font-bold px-6 py-2 rounded-lg shadow hover:bg-cyan-300 transition block mt-8 text-center">Hire KIKI for {service.title}</a>
      </div>
    </div>
  );
}
