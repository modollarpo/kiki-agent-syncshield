import { NextRequest, NextResponse } from 'next/server';
import { exchangeCodeForToken } from '../../../../backend/oauth_providers';
import { storeAccessToken } from '../../../../backend/syncshield_client';

// Exchange code for access token and store integration
export async function POST(req: NextRequest) {
  const { provider, code, userId } = await req.json();
  if (!provider || !code || !userId) return NextResponse.json({ error: 'Missing params' }, { status: 400 });
  try {
    const tokenResp = await exchangeCodeForToken(provider, code);
    const token = tokenResp.data.access_token || tokenResp.data.accessToken || tokenResp.data.token;
    if (!token) return NextResponse.json({ error: 'No access token returned' }, { status: 400 });
    await storeAccessToken(provider, userId, token);
    return NextResponse.json({ success: true, provider });
  } catch (e) {
    return NextResponse.json({ error: (e as Error).message }, { status: 400 });
  }
}
