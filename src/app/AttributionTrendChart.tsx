import React from "react";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions,
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

type AttributionHistory = {
  timestamp: string;
  ctr: number;
  conversions: number;
};

export const AttributionTrendChart: React.FC<{ history: AttributionHistory[] }> = ({ history }) => {
  if (!history.length) return <div className="text-zinc-400 text-xs">No data for chart.</div>;
  const labels = history.map(h => h.timestamp);
  const ctrData = history.map(h => h.ctr);
  const convData = history.map(h => h.conversions);

  const data = {
    labels,
    datasets: [
      {
        label: "CTR",
        data: ctrData,
        borderColor: "#10b981",
        backgroundColor: "rgba(16,185,129,0.2)",
        yAxisID: "y",
      },
      {
        label: "Conversions",
        data: convData,
        borderColor: "#6366f1",
        backgroundColor: "rgba(99,102,241,0.2)",
        yAxisID: "y1",
      },
    ],
  };

  const options: ChartOptions<"line"> = {
    responsive: true,
    plugins: {
      legend: { position: "top" },
      title: { display: true, text: "Attribution Trends" },
    },
    scales: {
      y: { type: "linear", display: true, position: "left", title: { display: true, text: "CTR" } },
      y1: { type: "linear", display: true, position: "right", title: { display: true, text: "Conversions" }, grid: { drawOnChartArea: false } },
    },
  };

  return <Line data={data} options={options} />;
};
