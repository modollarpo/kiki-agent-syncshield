import { useRouter } from 'next/router';
import CampaignOptimization from './campaign-optimization';
import RevenueAttribution from './revenue-attribution';

export default function ServicePage() {
  const router = useRouter();
  const { slug } = router.query;

  if (slug === 'campaign-optimization') return <CampaignOptimization />;
  if (slug === 'revenue-attribution') return <RevenueAttribution />;

  return (
    <div className="min-h-screen bg-zinc-950 text-white flex items-center justify-center">
      <div className="text-center">
        <h1 className="font-calsans text-4xl text-cyan-400 mb-4">Service Not Found</h1>
        <p className="font-intertight text-lg">Please select a valid KIKI Agent™ service.</p>
      </div>
    </div>
  );
}
