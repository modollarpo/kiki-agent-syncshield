import type { NextApiRequest, NextApiResponse } from 'next';

// This endpoint initiates OAuth for Ad API or CRM account linking
export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'POST') {
    const { provider } = req.body; // e.g., 'shopify', 'meta', 'google', 'hubspot', etc.
    // TODO: Implement OAuth URL generation and state tracking
    // For now, return mock URL
    res.status(200).json({
      url: `https://auth.kikiagent.com/oauth/${provider}?state=mockstate123`,
    });
  } else {
    res.status(405).end();
  }
}
