import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  // Wire up to real gRPC SyncTwin reject (mocked here)
  if (req.method === 'POST') {
    // TODO: Replace with gRPC client call
    res.status(200).json({ status: 'rejected' });
  } else {
    res.status(405).end();
  }
}
