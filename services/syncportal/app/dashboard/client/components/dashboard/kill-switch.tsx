import { useState } from 'react';
import { LucidePower } from 'lucide-react';

export function KillSwitch() {
  const [modalOpen, setModalOpen] = useState(false);
  const [paused, setPaused] = useState(false);

  const handleKill = () => {
    setPaused(true);
    setModalOpen(false);
    // TODO: Call backend API to trigger circuit breaker
  };

  return (
    <div className="bg-zinc-900 rounded-xl p-6 shadow-lg border border-zinc-800 flex flex-col items-center">
      <LucidePower className={`w-8 h-8 mb-2 ${paused ? 'text-red-500' : 'text-zinc-400'}`} />
      <h2 className="text-lg font-bold mb-2">Kill Switch</h2>
      <button
        className="bg-red-600 hover:bg-red-700 text-white font-semibold px-4 py-2 rounded-lg mt-2"
        onClick={() => setModalOpen(true)}
        disabled={paused}
      >
        {paused ? 'Paused' : 'Pause All Campaigns'}
      </button>
      {modalOpen && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
          <div className="bg-zinc-900 border border-zinc-700 rounded-xl p-8 shadow-xl flex flex-col items-center">
            <h3 className="text-xl font-bold mb-4">Confirm Pause</h3>
            <p className="mb-6 text-zinc-300">Are you sure you want to pause all campaigns? This will immediately halt all ad spend and creative deployment.</p>
            <div className="flex gap-4">
              <button
                className="bg-red-600 hover:bg-red-700 text-white font-semibold px-4 py-2 rounded-lg"
                onClick={handleKill}
              >
                Yes, Pause All
              </button>
              <button
                className="bg-zinc-700 hover:bg-zinc-600 text-white font-semibold px-4 py-2 rounded-lg"
                onClick={() => setModalOpen(false)}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
