import { UpliftChart } from './components/dashboard/uplift-chart';
import { TwinPrediction } from './components/dashboard/twin-prediction';
import { AuditLog } from './components/dashboard/audit-log';
import { ExplainabilityFeed } from './components/dashboard/explainability-feed';
import { SummaryStats } from './components/dashboard/summary-stats';
import { KillSwitch } from './components/dashboard/kill-switch';
import { IntegrationSetup } from './components/dashboard/integration-setup';

export default function ClientDashboardPage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 to-zinc-950 text-white px-6 py-8">
      <div className="max-w-7xl mx-auto space-y-8">
        <section>
          <SummaryStats />
        </section>
        <section className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <UpliftChart />
          <TwinPrediction />
        </section>
        <section className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <AuditLog />
          <ExplainabilityFeed />
          <KillSwitch />
        </section>
        <section>
          <IntegrationSetup />
        </section>
      </div>
    </main>
  );
}
