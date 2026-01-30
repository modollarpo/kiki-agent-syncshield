import { Chart } from "@/components/Chart";
import { useState } from "react";

const chartTypes = [
  { label: "Line", value: "line" },
  { label: "Bar", value: "bar" },
  { label: "Pie", value: "pie" },
];

export default function AnalyticsPage() {
  const [type, setType] = useState<"line" | "bar" | "pie">("line");

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Analytics</h1>
      <div className="flex gap-2 mb-4">
        {chartTypes.map((ct) => (
          <button
            key={ct.value}
            className={`px-3 py-1 rounded border ${type === ct.value ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"}`}
            onClick={() => setType(ct.value as any)}
          >
            {ct.label}
          </button>
        ))}
      </div>
      <Chart endpoint="/api/analytics" type={type} />
    </div>
  );
}
