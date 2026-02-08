import type { NextApiRequest, NextApiResponse } from 'next';

// Handles OAuth callback for Ad API/CRM account linking
export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  // Example: /api/onboarding/oauth-callback?provider=shopify&code=...&state=...
  const { provider, code, state } = req.query;
  // TODO: Exchange code for access token with provider, store in backend
  // For now, just return success
  res.status(200).json({ success: true, provider, code, state });
}
