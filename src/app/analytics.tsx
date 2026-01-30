"use client";
import { useState } from "react";

export function TimeRangeFilter({ onChange }: { onChange: (range: string) => void }) {
  const [range, setRange] = useState("24h");
  return (
    <div className="mb-4 flex gap-2 items-center">
      <label className="text-sm text-zinc-400">Time Range:</label>
      <select
        className="rounded bg-slate-800 text-white px-2 py-1"
        value={range}
        onChange={e => { setRange(e.target.value); onChange(e.target.value); }}
      >
        <option value="1h">1h</option>
        <option value="24h">24h</option>
        <option value="7d">7d</option>
        <option value="30d">30d</option>
      </select>
    </div>
  );
}

export function ExportCSV({ data, filename }: { data: any[]; filename: string }) {
  const handleExport = () => {
    const csv = [Object.keys(data[0]).join(",")].concat(data.map(row => Object.values(row).join(","))).join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };
  return (
    <button className="ml-2 px-3 py-1 rounded bg-emerald-700 text-white text-xs" onClick={handleExport}>
      Export CSV
    </button>
  );
}
