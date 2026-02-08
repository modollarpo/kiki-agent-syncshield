// Strict TypeScript definitions for KIKI Agent™ SyncPortal

export type AgentName =
  | 'SyncBrain'
  | 'SyncTwin'
  | 'SyncFlow'
  | 'SyncValue'
  | 'SyncCreate'
  | 'SyncEngage'
  | 'SyncShield'
  | 'SyncLedger'
  | 'SyncBill';

export interface BrandDNA {
  brandName: string;
  voice: string;
  valueProps: string[];
  visualLanguage: {
    primaryHex: string;
    secondaryHex: string;
  };
  audience: string;
  tone: string;
  complexity: string;
  socialProof: string[];
}

export interface NetProfitUplift {
  baselineRevenue: number;
  newRevenue: number;
  baselineAdSpend: number;
  newAdSpend: number;
  netProfitUplift: number;
  kikiFee: number;
}

export interface SyncTwinSimulation {
  confidenceScore: number;
  riskProfile: string;
  projectedNetProfitUplift: number;
}

export interface ExplainabilityLog {
  agent: AgentName;
  timestamp: string;
  message: string;
}
