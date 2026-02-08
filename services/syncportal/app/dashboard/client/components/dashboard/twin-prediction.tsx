import { LucideBrain, LucideAlertCircle } from 'lucide-react';

export function TwinPrediction() {
  // Example data, replace with real API call
  const prediction = {
    reach: 12000,
    ltvUplift: 3200,
    confidence: 0.91,
    approvalNeeded: true,
  };
  return (
    <div className="bg-zinc-900 rounded-xl p-6 shadow-lg border border-zinc-800 flex flex-col gap-3">
      <div className="flex items-center gap-2 mb-2">
        <LucideBrain className="w-6 h-6 text-sky-400" />
        <h2 className="text-lg font-bold">SyncTwin™ Simulation Gate</h2>
      </div>
      <div className="flex gap-8 text-lg">
        <div>
          <div className="font-semibold">Predicted Reach</div>
          <div className="text-sky-300">{prediction.reach.toLocaleString()}</div>
        </div>
        <div>
          <div className="font-semibold">Est. LTV Uplift</div>
          <div className="text-green-400">${prediction.ltvUplift.toLocaleString()}</div>
        </div>
        <div>
          <div className="font-semibold">Confidence</div>
          <div className="text-amber-400">{(prediction.confidence * 100).toFixed(1)}%</div>
        </div>
      </div>
      {prediction.approvalNeeded && (
        <div className="flex items-center gap-2 mt-4 bg-amber-900/60 border border-amber-700 rounded-lg px-3 py-2">
          <LucideAlertCircle className="w-5 h-5 text-amber-400" />
          <span className="text-amber-200 font-medium">Approval Needed: Review and approve new strategy before launch.</span>
        </div>
      )}
    </div>
  );
}
