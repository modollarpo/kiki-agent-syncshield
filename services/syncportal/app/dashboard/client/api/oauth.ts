// OAuth utility for ad platform/CRM integrations
import axios from 'axios';

export async function startOAuth(provider: string) {
  // Redirect to backend OAuth endpoint
  window.location.href = `/api/integrations/oauth/start?provider=${provider}`;
}

export async function completeOAuth(provider: string, code: string) {
  // Exchange code for access token
  const { data } = await axios.post('/api/integrations/oauth/complete', { provider, code });
  return data;
}
