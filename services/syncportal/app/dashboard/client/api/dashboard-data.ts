// API utility for fetching live dashboard data
import axios from 'axios';

export async function fetchSummaryStats() {
  const { data } = await axios.get('/api/dashboard/summary-stats');
  return data;
}

export async function fetchUpliftChart() {
  const { data } = await axios.get('/api/dashboard/uplift-chart');
  return data;
}

export async function fetchTwinPrediction() {
  const { data } = await axios.get('/api/dashboard/twin-prediction');
  return data;
}

export async function fetchAuditLog() {
  const { data } = await axios.get('/api/dashboard/audit-log');
  return data;
}

export async function fetchExplainabilityFeed() {
  const { data } = await axios.get('/api/dashboard/explainability-feed');
  return data;
}

export async function fetchIntegrations() {
  const { data } = await axios.get('/api/dashboard/integrations');
  return data;
}
