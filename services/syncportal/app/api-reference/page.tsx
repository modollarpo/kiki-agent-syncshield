import Link from 'next/link';

export default function APIReference() {
  return (
    <div className="min-h-screen bg-zinc-950 text-white flex flex-col items-center justify-center">
      <div className="w-full max-w-2xl px-8 py-16 text-center">
        <h1 className="font-calsans text-4xl text-cyan-400 mb-6">
          REST & gRPC API Reference
        </h1>
        <p className="text-lg mb-8 font-intertight">
          Explore the full API for KIKI Agent™. All endpoints are strongly typed, auditable, and compliant with SOC2, GDPR, and ISO 27001.
        </p>
        <ul className="text-left text-lg mb-8 font-intertight list-disc list-inside">
          <li>Onboarding: <span className="text-cyan-300">POST /onboarding</span></li>
          <li>Brand DNA Extraction: <span className="text-cyan-300">POST /brand-dna</span></li>
          <li>Account Linking: <span className="text-cyan-300">POST /account-link</span></li>
          <li>Campaign Optimization: <span className="text-cyan-300">POST /campaign-optimize</span></li>
          <li>Revenue Attribution: <span className="text-cyan-300">GET /revenue-attribution</span></li>
          <li>Audit Trail: <span className="text-cyan-300">GET /audit-events</span></li>
        </ul>
        <div className="flex flex-row gap-6 justify-center mb-8">
          <Link href="/integration-ecosystem" className="bg-cyan-400 text-zinc-950 font-bold px-6 py-3 rounded-xl shadow-lg hover:bg-cyan-300 transition">
            Integration Ecosystem
          </Link>
          <Link href="/onboarding" className="bg-zinc-800 text-cyan-400 font-bold px-6 py-3 rounded-xl shadow-lg hover:bg-zinc-700 transition">
            Begin Onboarding
          </Link>
        </div>
        <div className="text-xs text-zinc-500 mt-12">
          For full OpenAPI and gRPC schemas, see <Link href="/openapi/openapi.yaml" className="underline text-cyan-300">openapi.yaml</Link> and <Link href="/schemas" className="underline text-cyan-300">/schemas</Link>.
        </div>
      </div>
      <footer className="mt-16 text-xs text-zinc-500">
        SOC2 Type II • ISO 27001 • GDPR • Immutable Audit Logs • Integration Ecosystem: Shopify, Meta, Google, Salesforce, Stripe • © 2026 KIKI™ Enterprise Platform.
      </footer>
    </div>
  );
}
