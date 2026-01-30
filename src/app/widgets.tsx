"use client";
import { useEffect, useState } from "react";
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { motion } from "framer-motion";
import {
  fetchSyncBrainStatus,
  fetchSyncValueStatus,
  fetchSyncFlowStatus,
  fetchSyncCreateStatus,
  fetchSyncShieldStatus,
  connectNeuralFeed,
} from "./api";

// KPI Card
export function KPI({ label, value, pulse }: { label: string; value: string | number; pulse?: boolean }) {
  return (
    <div className="col-span-1 rounded-xl p-4 backdrop-blur-md bg-slate-900/50 border border-slate-800 flex flex-col items-center">
      <div className="font-semibold mb-1 flex items-center gap-2">
        {label}
        {pulse && (
          <motion.span
            className="inline-block w-2 h-2 rounded-full bg-emerald-400"
            animate={{ opacity: [0.5, 1, 0.5] }}
            transition={{ repeat: Infinity, duration: 1.2 }}
          />
        )}
      </div>
      <div className="text-2xl font-bold">{value}</div>
    </div>
  );
}

// Revenue Impact Area Chart (with confidence band)
export function RevenueChart({ data, lowConfidence }: { data: any[]; lowConfidence: boolean }) {
  return (
    <div className="rounded-xl p-4 backdrop-blur-md bg-slate-900/50 border border-slate-800 mb-8">
      <div className="font-semibold mb-2">Revenue Impact</div>
      <ResponsiveContainer width="100%" height={200}>
        <AreaChart data={data} margin={{ left: 0, right: 0, top: 10, bottom: 0 }}>
          <XAxis dataKey="time" hide />
          <YAxis hide />
          <Tooltip />
          <Area
            type="monotone"
            dataKey="revenue"
            stroke={lowConfidence ? "orange" : "#10b981"}
            fill={lowConfidence ? "#fbbf24" : "#10b981"}
            fillOpacity={0.2}
            strokeWidth={3}
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
      {lowConfidence && <div className="text-orange-400 text-xs mt-1">Low confidence: check data</div>}
    </div>
  );
}

// Neural Feed Terminal
export function NeuralFeedTerminal({ feed }: { feed: string[] }) {
  return (
    <div className="rounded-xl p-4 backdrop-blur-md bg-slate-900/50 border border-slate-800 mb-8">
      <div className="font-semibold mb-2">Neural Feed (SyncBrain SSE)</div>
      <div className="h-40 overflow-y-auto font-mono text-xs bg-black/30 p-2 rounded">
        {feed.length === 0 ? <div>Waiting for data...</div> : feed.map((msg, i) => <div key={i}>{msg}</div>)}
      </div>
    </div>
  );
}

// Asset Gallery (SyncCreate)
export function AssetGallery({ assets }: { assets: string[] }) {
  return (
    <div className="rounded-xl p-4 backdrop-blur-md bg-slate-900/50 border border-slate-800 mb-8">
      <div className="font-semibold mb-2">Asset Gallery</div>
      <div className="flex flex-wrap gap-2">
        {assets.length === 0 ? <div>No assets yet.</div> : assets.map((url, i) => <img key={i} src={url} alt="asset" className="w-20 h-20 rounded object-cover" />)}
      </div>
    </div>
  );
}

// Risk Audit Log (SyncShield)
export function RiskAuditLog({ logs }: { logs: string[] }) {
  return (
    <div className="rounded-xl p-4 backdrop-blur-md bg-slate-900/50 border border-slate-800 mb-8">
      <div className="font-semibold mb-2">Risk Audit Log</div>
      <div className="h-32 overflow-y-auto font-mono text-xs bg-black/30 p-2 rounded">
        {logs.length === 0 ? <div>No audit events.</div> : logs.map((msg, i) => <div key={i}>{msg}</div>)}
      </div>
    </div>
  );
}

// Intervention Button
export function InterventionButton({ onClick, paused }: { onClick: () => void; paused: boolean }) {
  return (
    <button
      className={`rounded px-4 py-2 font-semibold mt-2 ${paused ? "bg-orange-500" : "bg-emerald-600"} text-white hover:opacity-80`}
      onClick={onClick}
    >
      {paused ? "Resume Bidding" : "Pause Bidding"}
    </button>
  );
}
