"use client";
"use client";
import { useState } from "react";

export function DrillDownModal({ open, onClose, title, children }: { open: boolean; onClose: () => void; title: string; children: React.ReactNode }) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
      <div className="bg-slate-900 p-8 rounded-xl shadow-xl min-w-100 max-w-[90vw] max-h-[90vh] overflow-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-emerald-400">{title}</h2>
          <button className="text-white text-2xl ml-4" onClick={onClose}>×</button>
        </div>
        {children}
      </div>
    </div>
  );
}
