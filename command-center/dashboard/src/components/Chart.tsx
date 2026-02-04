"use client";
import { useEffect, useState, useRef } from "react";
import { Skeleton } from "@/components/ui/skeleton";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Brush,
} from "recharts";

const COLORS = [
  "#6366f1",
  "#10b981",
  "#f59e42",
  "#ef4444",
  "#3b82f6",
  "#a78bfa",
  "#f472b6",
  "#22d3ee",
  "#facc15",
  "#4ade80",
];

function exportCSV(data: any[], metrics: string[]) {
  const header = ["name", ...metrics];
  const rows = data.map((row) =>
    header.map((h) => row[h] ?? "").join(",")
  );
  const csvContent =
    "data:text/csv;charset=utf-8," +
    [header.join(","), ...rows].join("\n");
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement("a");
  link.setAttribute("href", encodedUri);
  link.setAttribute("download", "analytics.csv");
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

function exportPNG(ref: React.RefObject<HTMLDivElement | null>) {
  const element = ref.current;
  if (!element) return;
  import("html2canvas").then(({ default: html2canvas }) => {
    html2canvas(element).then((canvas) => {
      const link = document.createElement("a");
      link.download = "chart.png";
      link.href = canvas.toDataURL();
      link.click();
    });
  });
}

function CustomTooltip({ active, payload, label }: any) {
  if (active && payload && payload.length) {
    return (
      <div className="bg-popover p-2 rounded shadow text-xs">
        <div className="font-bold mb-1">{label}</div>
        {payload.map((entry: any, idx: number) => (
          <div key={idx} style={{ color: entry.color }}>
            {entry.name}: <span className="font-mono">{entry.value}</span>
          </div>
        ))}
      </div>
    );
  }
  return null;
}

export function Chart({
  endpoint = "/api/analytics",
  type = "line",
}: {
  endpoint?: string;
  type?: "line" | "bar" | "pie";
}) {
  const [data, setData] = useState<any[]>([]);
  const [metrics, setMetrics] = useState<string[]>([]);
  const [activeIndex, setActiveIndex] = useState<number | null>(null);
  const chartRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetch(endpoint)
      .then((res) => res.json())
      .then((d) => {
        if (
          Array.isArray(d.analytics) &&
          d.analytics.length > 0 &&
          typeof d.analytics[0] === "object"
        ) {
          setData(d.analytics);
          setMetrics(
            Object.keys(d.analytics[0]).filter((k) => k !== "name")
          );
        } else if (Array.isArray(d.analytics)) {
          setData(
            d.analytics.map((v: number, i: number) => ({
              name: `Metric ${i + 1}`,
              value: v,
            }))
          );
          setMetrics(["value"]);
        } else {
          setData([]);
          setMetrics([]);
        }
      });
  }, [endpoint]);

  if (data.length === 0) {
    return <Skeleton className="h-24 w-full" />;
  }

  return (
    <div className="bg-card p-4 rounded-lg border border-border h-96">
      <div className="flex gap-2 mb-2">
        <button
          className="px-2 py-1 rounded border bg-primary text-primary-foreground text-xs"
          onClick={() => exportCSV(data, metrics)}
        >
          Export CSV
        </button>
        <button
          className="px-2 py-1 rounded border bg-secondary text-secondary-foreground text-xs"
          onClick={() => exportPNG(chartRef)}
        >
          Export PNG
        </button>
      </div>
      <div ref={chartRef} className="h-80">
        <ResponsiveContainer width="100%" height={300}>
          {type === "line" && (
            <LineChart
              data={data}
              onClick={(e) =>
                setActiveIndex(
                  e && typeof e.activeTooltipIndex === "number" ? e.activeTooltipIndex : null
                )
              }
            >
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ fontSize: "12px" }} />
              <Brush dataKey="name" height={20} stroke="#6366f1" />
              {metrics.map((m, idx) => (
                <Line
                  key={m}
                  type="monotone"
                  dataKey={m}
                  stroke={COLORS[idx % COLORS.length]}
                  strokeWidth={3}
                  activeDot={{ r: 8 }}
                />
              ))}
            </LineChart>
          )}
          {type === "bar" && (
            <BarChart
              data={data}
              onClick={(e) =>
                setActiveIndex(
                  e && typeof e.activeTooltipIndex === "number" ? e.activeTooltipIndex : null
                )
              }
            >
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ fontSize: "12px" }} />
              <Brush dataKey="name" height={20} stroke="#10b981" />
              {metrics.map((m, idx) => (
                <Bar key={m} dataKey={m} fill={COLORS[idx % COLORS.length]} />
              ))}
            </BarChart>
          )}
          {type === "pie" && (
            <PieChart>
              <Tooltip content={<CustomTooltip />} />
              <Legend wrapperStyle={{ fontSize: "12px" }} />
              {metrics.map((m, idx) => (
                <Pie
                  key={m}
                  data={data}
                  dataKey={m}
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={80 - idx * 15}
                  label
                >
                  {data.map((entry, i) => (
                    <Cell key={`cell-${i}`} fill={COLORS[i % COLORS.length]} />
                  ))}
                </Pie>
              ))}
            </PieChart>
          )}
        </ResponsiveContainer>
      </div>
      {activeIndex !== null && (
        <div className="mt-2 text-sm text-primary">
          <strong>Selected:</strong> {JSON.stringify(data[activeIndex])}
        </div>
      )}
    </div>
  );
}
