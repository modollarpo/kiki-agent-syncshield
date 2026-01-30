import { NeuralLog } from "@/components/NeuralLog";

export default function LogsPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Neural Log</h1>
      <NeuralLog endpoint="ws://localhost:8001/api/logs" />
    </div>
  );
}
