import type { NextApiRequest, NextApiResponse } from 'next';

// This endpoint proxies to SyncCreate for creative generation
export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'POST') {
    // TODO: Replace with real gRPC call to SyncCreate
    res.status(200).json({
      creatives: [
        { id: 'creative1', url: 'https://cdn.kikiagent.com/creative1.png', type: 'image' },
        { id: 'creative2', url: 'https://cdn.kikiagent.com/creative2.png', type: 'image' },
      ],
      adCopy: [
        'Discover your best self with Rare Beauty.',
        'Beauty for every shade and story.',
      ],
    });
  } else {
    res.status(405).end();
  }
}
