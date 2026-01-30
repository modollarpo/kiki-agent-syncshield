import React from "react";

export const LegalConsent: React.FC = () => {
  return (
    <div className="space-y-4 p-6 bg-slate-800 rounded-lg">
      <div className="flex items-start gap-3">
        <input type="checkbox" id="terms" className="mt-1" />
        <label htmlFor="terms" className="text-sm text-slate-300">
          I authorize KIKI to manage my ad spend and generate creative assets 
          based on the <b>Risk Appetite</b> I have configured.
        </label>
      </div>
      <div className="flex items-start gap-3">
        <input type="checkbox" id="privacy" className="mt-1" />
        <label htmlFor="privacy" className="text-sm text-slate-300">
          I understand that my data will be processed by 9 autonomous agents 
          to optimize LTV, as described in the <b>Privacy Policy</b>.
        </label>
      </div>
      <button className="w-full py-3 bg-emerald-500 hover:bg-emerald-600 text-white font-bold rounded-lg transition-all">
        Finalize & Deploy Council of Nine
      </button>
    </div>
  );
}
