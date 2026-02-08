import type { NextApiRequest, NextApiResponse } from 'next';

// This endpoint checks if Ad API or CRM account is linked
export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'GET') {
    const { provider } = req.query;
    // TODO: Check backend for linked account status
    // For now, return mock status
    res.status(200).json({
      linked: provider === 'shopify' || provider === 'meta',
      provider,
    });
  } else {
    res.status(405).end();
  }
}
