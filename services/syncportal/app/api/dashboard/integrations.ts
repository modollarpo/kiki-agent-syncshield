import { NextResponse } from 'next/server';

// TODO: Replace with real integration status from backend
export async function GET() {
  const integrations = [
    { name: 'Meta Ads', status: 'connected', provider: 'meta' },
    { name: 'Google Ads', status: 'connected', provider: 'google' },
    { name: 'TikTok Ads', status: 'not_connected', provider: 'tiktok' },
    { name: 'Shopify', status: 'connected', provider: 'shopify' },
    { name: 'HubSpot', status: 'not_connected', provider: 'hubspot' },
  ];
  return NextResponse.json(integrations);
}
