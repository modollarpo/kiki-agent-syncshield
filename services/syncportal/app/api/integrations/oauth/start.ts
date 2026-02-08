import { NextRequest, NextResponse } from 'next/server';
import { getOAuthUrl } from '../../../../backend/oauth_providers';

// Redirect user to provider's OAuth URL
export async function GET(req: NextRequest) {
  const provider = req.nextUrl.searchParams.get('provider');
  if (!provider) return NextResponse.json({ error: 'Missing provider' }, { status: 400 });
  // Generate a state param for CSRF protection (could be user/session ID)
  const state = Math.random().toString(36).substring(2);
  try {
    const oauthUrl = await getOAuthUrl(provider, state);
    return NextResponse.redirect(oauthUrl);
  } catch (e) {
    return NextResponse.json({ error: (e as Error).message }, { status: 400 });
  }
}
