import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'POST') {
    // TODO: Replace with real backend/gRPC call to SyncScrape
    // For now, mock response
    res.status(200).json({
      brandName: 'Rare Beauty',
      voice: 'Inclusive, authentic, uplifting',
      valueProps: ['Cruelty-free', 'Mental health advocacy', 'Accessible beauty'],
      visualLanguage: { primaryHex: '#F7CAC9', secondaryHex: '#92A8D1' },
      audience: 'Gen-Z, Millennial, High-Intent Beauty Shoppers',
      tone: 'Empowering',
      complexity: 'Conversational',
      socialProof: ['4.8/5 reviews', 'Sephora Best Seller'],
    });
  } else {
    res.status(405).end();
  }
}
