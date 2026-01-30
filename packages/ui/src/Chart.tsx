import React from "react";

export interface ChartProps {
  title?: string;
  data: { label: string; value: number }[];
  className?: string;
}

/**
 * Enterprise Chart — High-Trust, Dark-Mode, Emerald Accents
 * Simple bar chart for quick metrics visualization.
 */
export const Chart: React.FC<ChartProps> = ({ title, data, className = "" }) => {
  const max = Math.max(...data.map(d => d.value), 1);
  return (
    <div className={`bg-slate-900 border border-emerald-500/30 rounded-2xl p-6 shadow-xl ${className}`}>
      {title && <h3 className="text-lg font-bold text-emerald-400 mb-4 font-sans">{title}</h3>}
      <div className="space-y-3">
        {data.map((d, i) => (
          <div key={d.label} className="flex items-center gap-4">
            <span className="w-24 text-slate-300 font-mono text-xs">{d.label}</span>
            <div className="flex-1 h-4 bg-slate-800 rounded-lg overflow-hidden">
              <div
                className="h-4 bg-gradient-to-r from-emerald-500 to-emerald-300 rounded-lg transition-all"
                style={{ width: `${(d.value / max) * 100}%` }}
              />
            </div>
            <span className="w-12 text-right text-emerald-400 font-bold font-mono">{d.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Chart;
