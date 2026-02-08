// Provider-specific OAuth logic for Meta, Google, TikTok, Shopify, HubSpot
import axios from 'axios';

export async function getOAuthUrl(provider: string, state: string) {
  switch (provider) {
    case 'meta':
      return `https://www.facebook.com/v18.0/dialog/oauth?client_id=${process.env.META_CLIENT_ID}&redirect_uri=${process.env.OAUTH_REDIRECT_URI}&state=${state}&scope=ads_management,business_management`;
    case 'google':
      return `https://accounts.google.com/o/oauth2/v2/auth?client_id=${process.env.GOOGLE_CLIENT_ID}&redirect_uri=${process.env.OAUTH_REDIRECT_URI}&response_type=code&scope=https://www.googleapis.com/auth/adwords&state=${state}`;
    case 'tiktok':
      return `https://ads.tiktok.com/marketing_api/oauth?app_id=${process.env.TIKTOK_CLIENT_ID}&redirect_uri=${process.env.OAUTH_REDIRECT_URI}&state=${state}&scope=ads.read,ads.write`;
    case 'shopify':
      return `https://accounts.shopify.com/oauth/authorize?client_id=${process.env.SHOPIFY_CLIENT_ID}&redirect_uri=${process.env.OAUTH_REDIRECT_URI}&scope=read_orders,read_customers&state=${state}`;
    case 'hubspot':
      return `https://app.hubspot.com/oauth/authorize?client_id=${process.env.HUBSPOT_CLIENT_ID}&redirect_uri=${process.env.OAUTH_REDIRECT_URI}&scope=contacts%20content&state=${state}`;
    default:
      throw new Error('Unknown provider');
  }
}

export async function exchangeCodeForToken(provider: string, code: string) {
  switch (provider) {
    case 'meta':
      return axios.post('https://graph.facebook.com/v18.0/oauth/access_token', {
        client_id: process.env.META_CLIENT_ID,
        client_secret: process.env.META_CLIENT_SECRET,
        redirect_uri: process.env.OAUTH_REDIRECT_URI,
        code,
      });
    case 'google':
      return axios.post('https://oauth2.googleapis.com/token', {
        client_id: process.env.GOOGLE_CLIENT_ID,
        client_secret: process.env.GOOGLE_CLIENT_SECRET,
        redirect_uri: process.env.OAUTH_REDIRECT_URI,
        code,
        grant_type: 'authorization_code',
      });
    case 'tiktok':
      return axios.post('https://business-api.tiktok.com/open_api/v1.3/oauth2/access_token/', {
        app_id: process.env.TIKTOK_CLIENT_ID,
        secret: process.env.TIKTOK_CLIENT_SECRET,
        auth_code: code,
        grant_type: 'authorized_code',
      });
    case 'shopify':
      return axios.post(`https://${process.env.SHOPIFY_SHOP}/admin/oauth/access_token`, {
        client_id: process.env.SHOPIFY_CLIENT_ID,
        client_secret: process.env.SHOPIFY_CLIENT_SECRET,
        code,
      });
    case 'hubspot':
      return axios.post('https://api.hubapi.com/oauth/v1/token', {
        client_id: process.env.HUBSPOT_CLIENT_ID,
        client_secret: process.env.HUBSPOT_CLIENT_SECRET,
        redirect_uri: process.env.OAUTH_REDIRECT_URI,
        code,
        grant_type: 'authorization_code',
      });
    default:
      throw new Error('Unknown provider');
  }
}
