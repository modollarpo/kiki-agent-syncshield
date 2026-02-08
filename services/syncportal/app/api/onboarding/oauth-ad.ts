import type { NextApiRequest, NextApiResponse } from 'next';

// This endpoint would redirect to the real OAuth flow for the selected ad platform
export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'POST') {
    // TODO: Implement real OAuth redirect/flow for Meta, Google, TikTok, etc.
    // For now, mock success
    res.status(200).json({ status: 'ad_connected', platform: req.body?.platform || 'meta' });
  } else {
    res.status(405).end();
  }
}
