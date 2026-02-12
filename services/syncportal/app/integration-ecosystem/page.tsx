import Link from 'next/link';

export default function IntegrationEcosystem() {
  return (
    <div className="min-h-screen bg-zinc-950 text-white flex flex-col items-center justify-center">
      <div className="w-full max-w-2xl px-8 py-16 text-center">
        <h1 className="font-calsans text-4xl text-cyan-400 mb-6">
          Integration Ecosystem
        </h1>
        <p className="text-lg mb-8 font-intertight">
          Seamlessly connect your CRM, CMS, and Ad platforms for full-funnel orchestration and compliance. KIKI Agent™ supports:
        </p>
        <ul className="text-left text-lg mb-8 font-intertight list-disc list-inside">
          <li>Shopify, WooCommerce, BigCommerce</li>
          <li>Meta Ads, Google Ads, TikTok Ads, LinkedIn Ads, Amazon Ads, Microsoft Ads</li>
          <li>Salesforce, HubSpot, Klaviyo, Mailchimp</li>
          <li>Stripe, PayPal, ACH, Digital Wallets</li>
        </ul>
        <div className="flex flex-row gap-6 justify-center mb-8">
          <Link href="/onboarding" className="bg-cyan-400 text-zinc-950 font-bold px-6 py-3 rounded-xl shadow-lg hover:bg-cyan-300 transition">
            Begin Integration Onboarding
          </Link>
          <Link href="/api-reference" className="bg-zinc-800 text-cyan-400 font-bold px-6 py-3 rounded-xl shadow-lg hover:bg-zinc-700 transition">
            View API Reference
          </Link>
        </div>
        <div className="text-xs text-zinc-500 mt-12">
          All integrations are SOC2, GDPR, and ISO 27001 compliant. Immutable audit logs are maintained for every event.
        </div>
      </div>
      <footer className="mt-16 text-xs text-zinc-500">
        © 2026 KIKI™ Enterprise Platform.
      </footer>
    </div>
  );
}
