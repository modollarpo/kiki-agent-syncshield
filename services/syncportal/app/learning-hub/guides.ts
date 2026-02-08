export const guides = [
  {
    slug: 'oaas-explained',
    title: 'What is Outcome-as-a-Service (OaaS)?',
    description: 'A deep dive into the OaaS model and why it aligns incentives for both clients and providers.',
    author: 'KIKI Editorial',
    date: '2026-02-08',
    content: `Outcome-as-a-Service (OaaS) is a performance-first model where you only pay for measurable profit uplift.\n\nKIKI Agent™ calculates Net Profit Uplift as:\n(New Revenue - Baseline Revenue) - (New Ad Spend - Baseline Ad Spend)\n\nThis ensures that every dollar spent is tracked, and only profitable outcomes are billed.\n\nOaaS aligns incentives: If ad costs eat profit, KIKI doesn’t get paid.\n\nLearn more in the dashboard or try the ROI Calculator.`,
  },
  {
    slug: 'synctwin-prediction',
    title: 'SyncTwin™: Predicting Profit Before Spend',
    description: 'How simulation and risk management drive performance-based marketing.',
    author: 'KIKI Editorial',
    date: '2026-02-07',
    content: `SyncTwin™ is the gatekeeper for every campaign. It simulates thousands of scenarios before launch, including market shocks and conversion drops.\n\nIf projected Net Profit Uplift is negative, the campaign is blocked.\n\nThis protects both the client and KIKI’s OaaS fee.\n\nSyncTwin™ also monitors live performance, auto-pausing campaigns if deviation exceeds 15%.\n\nThis is digital insurance for marketing.`,
  },
  {
    slug: 'ad-api-guide',
    title: 'How KIKI Connects to Ad APIs',
    description: 'Technical overview of OAuth, permissions, and data sync for Meta, Google, TikTok, and more.',
    author: 'KIKI Editorial',
    date: '2026-02-08',
    content: `KIKI Agent™ uses secure OAuth flows to connect to your ad platforms.\n\nSupported platforms: Meta, Google, TikTok, LinkedIn, Amazon, Microsoft.\n\n1. Click Connect in onboarding.\n2. Approve permissions for campaign management and reporting.\n3. KIKI stores credentials encrypted (AES-256, SOC2/GDPR compliant).\n4. Data is synced in real time for optimization and attribution.\n\nNo credentials are ever shared with third parties.`,
  },
  {
    slug: 'crm-guide',
    title: 'CRM Data: The Secret to LTV',
    description: 'How CRM integration powers LTV prediction, retention, and OaaS billing.',
    author: 'KIKI Editorial',
    date: '2026-02-08',
    content: `CRM data lets KIKI Agent™:
- Predict customer LTV
- Trigger retention automations
- Attribute revenue to the right campaign
- Power OaaS billing with real transaction data

Connect your CRM in onboarding. All data is encrypted and SOC2/GDPR compliant.`
  }
];
