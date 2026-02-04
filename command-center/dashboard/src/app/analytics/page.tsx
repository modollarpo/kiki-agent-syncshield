"use client";

import { Chart } from "@/components/Chart";
import { useState } from "react";

const chartTypes = [
  { label: "Line", value: "line" as const },
  { label: "Bar", value: "bar" as const },
  { label: "Pie", value: "pie" as const },
] as const;

type ChartType = (typeof chartTypes)[number]["value"];

export default function AnalyticsPage() {
  const [type, setType] = useState<ChartType>("line");

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Analytics</h1>
      <div className="flex gap-2 mb-4">
        {chartTypes.map((ct) => (
          <button
            key={ct.value}
            className={`px-3 py-1 rounded border ${type === ct.value ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"}`}
            onClick={() => setType(ct.value)}
          >
            {ct.label}
          </button>
        ))}
      </div>
      <Chart endpoint="/api/analytics" type={type} />
    </div>
  );
}
