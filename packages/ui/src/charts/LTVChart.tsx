import React from 'react';
import { colors } from '../theme';

export interface LTVChartProps {
  data: { date: string; ltv: number; roas?: number }[];
  height?: number;
}

export const LTVChart: React.FC<LTVChartProps> = ({ data, height = 240 }) => {
  // Simple SVG line chart for LTV (production: use recharts, nivo, etc.)
  if (!data.length) return <div style={{ height }}>No data</div>;
  const maxLTV = Math.max(...data.map(d => d.ltv));
  const minLTV = Math.min(...data.map(d => d.ltv));
  const points = data.map((d, i) => {
    const x = (i / (data.length - 1)) * 400;
    const y = height - ((d.ltv - minLTV) / (maxLTV - minLTV || 1)) * (height - 40) - 20;
    return `${x},${y}`;
  });
  return (
    <svg width={420} height={height} style={{ background: colors.neutral[100], borderRadius: 8 }}>
      {/* LTV line */}
      <polyline
        fill="none"
        stroke={colors.primary[500]}
        strokeWidth={3}
        points={points.join(' ')}
      />
      {/* Dots */}
      {data.map((d, i) => {
        const [x, y] = points[i].split(',').map(Number);
        return (
          <circle key={i} cx={x} cy={y} r={4} fill={colors.primary[500]} />
        );
      })}
      {/* Axes */}
      <line x1={20} y1={height - 20} x2={400} y2={height - 20} stroke={colors.neutral[400]} />
      <line x1={20} y1={20} x2={20} y2={height - 20} stroke={colors.neutral[400]} />
      {/* Labels */}
      <text x={10} y={30} fontSize={12} fill={colors.neutral[600]}>LTV</text>
      <text x={400} y={height - 5} fontSize={12} fill={colors.neutral[600]}>Date</text>
    </svg>
  );
};
