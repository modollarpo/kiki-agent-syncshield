// SyncReflex Attribution API
export async function sendAttribution(creativeId: string, ctr: number, conversions: number, platform: string, style: string) {
  const res = await fetch("http://localhost:8008/attribution", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ creative_id: creativeId, ctr, conversions, platform, style })
  });
  return await res.json();
}

export async function getPerformance(creativeId: string) {
  const res = await fetch(`http://localhost:8008/performance/${creativeId}`);
  return await res.json();
}

// SyncTwin Simulation API
export async function runBidSimulation(bidAmount: number, impressions: number, platform: string) {
  const res = await fetch("http://localhost:8007/simulate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ bid_amount: bidAmount, impressions, platform })
  });
  return await res.json();
}
// Fetch CRM event log from API gateway
export async function fetchCrmEventLog() {
  const res = await fetch(`${API_GATEWAY}/api/syncengage/events`);
  if (!res.ok) throw new Error("Failed to fetch CRM event log");
  return await res.json();
}
// Fetch creative history from API gateway
export async function fetchCreativeHistory() {
  const res = await fetch(`${API_GATEWAY}/api/synccreate/creatives`);
  if (!res.ok) throw new Error("Failed to fetch creative history");
  return await res.json();
}
// API utility for connecting to backend services

// Health endpoints

// --- API Gateway Integration for SyncCreate and SyncEngage ---
const API_GATEWAY = "http://localhost:8080";

export async function generateCreative(prompt: string, userId: string, style = "default", numImages = 1) {
  const res = await fetch(`${API_GATEWAY}/api/synccreate/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt, user_id: userId, style, num_images: numImages })
  });
  if (!res.ok) throw new Error("Creative generation failed");
  return await res.json();
}

export async function triggerCRMEvent(event: string, payload: any) {
  const res = await fetch(`${API_GATEWAY}/api/syncengage/${event}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error("CRM event failed");
  return await res.json();
}
export async function fetchSyncBrainStatus() {
  try {
    const res = await fetch("http://localhost:8001/healthz");
    return res.text();
  } catch {
    return "unreachable";
  }
}
export async function fetchSyncValueStatus() {
  try {
    const res = await fetch("http://localhost:8002/healthz");
    return res.text();
  } catch {
    return "unreachable";
  }
}
export async function fetchSyncFlowStatus() {
  try {
    const res = await fetch("http://localhost:8003/healthz");
    return res.text();
  } catch {
    return "unreachable";
  }
}
export async function fetchSyncCreateStatus() {
  try {
    const res = await fetch("http://localhost:8004/healthz");
    return res.text();
  } catch {
    return "unreachable";
  }
}
export async function fetchSyncShieldStatus() {
  try {
    const res = await fetch("http://localhost:8005/healthz");
    return res.text();
  } catch {
    return "unreachable";
  }
}

// Real API endpoints for widgets
export async function fetchLTV() {
  try {
    const res = await fetch("http://localhost:8002/ltv");
    const data = await res.json();
    return data.ltv;
  } catch {
    return Math.round(1000 + Math.random() * 500); // fallback demo
  }
}
export async function fetchBidsExecuted() {
  try {
    const res = await fetch("http://localhost:8003/bids");
    const data = await res.json();
    return data.count;
  } catch {
    return Math.floor(Math.random() * 10000); // fallback demo
  }
}
export async function fetchComplianceScore() {
  try {
    const res = await fetch("http://localhost:8005/compliance");
    const data = await res.json();
    return data.score;
  } catch {
    return 100 - Math.floor(Math.random() * 5); // fallback demo
  }
}
export async function fetchActiveAgents() {
  // Could aggregate from health endpoints
  return 5;
}
export async function fetchRevenueData() {
  try {
    const res = await fetch("http://localhost:8003/revenue");
    const data = await res.json();
    return data.history;
  } catch {
    // fallback demo
    return Array.from({ length: 30 }, (_, i) => ({ time: `${i}:00`, revenue: 1000 + Math.random() * 500 }));
  }
}
export async function fetchConfidence() {
  try {
    const res = await fetch("http://localhost:8002/confidence");
    const data = await res.json();
    return data.low;
  } catch {
    return Math.random() < 0.1;
  }
}
export async function fetchAssets() {
  try {
    const res = await fetch("http://localhost:8004/assets");
    const data = await res.json();
    return data.assets;
  } catch {
    return ["/asset1.png", "/asset2.png"];
  }
}
export async function fetchAuditLogs() {
  try {
    const res = await fetch("http://localhost:8005/audit/logs");
    const data = await res.json();
    return data.logs;
  } catch {
    return [
      `Audit event at ${new Date().toLocaleTimeString()}`,
      `Audit event at ${new Date().toLocaleTimeString()}`,
    ];
  }
}
export async function sendIntervention(paused: boolean) {
  try {
    await fetch(`http://localhost:8003/${paused ? "pause" : "resume"}`, { method: "POST" });
  } catch {}
}

// Example: SSE for neural feed
export function connectNeuralFeed(onMessage: (msg: string) => void) {
  const evtSource = new EventSource("http://localhost:8001/neural-feed");
  evtSource.onmessage = (e) => onMessage(e.data);
  return evtSource;
}
