import type { NextApiRequest, NextApiResponse } from 'next';

// This endpoint would redirect to the real OAuth flow for the selected CRM
export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'POST') {
    // TODO: Implement real OAuth redirect/flow for HubSpot, Salesforce, etc.
    // For now, mock success
    res.status(200).json({ status: 'crm_connected', platform: req.body?.platform || 'hubspot' });
  } else {
    res.status(405).end();
  }
}
