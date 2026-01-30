import React, { useState } from 'react';

export const OaasCalculator: React.FC = () => {
	const [revenue, setRevenue] = useState(100000); // Current Revenue
	const [lift, setLift] = useState(20); // Expected % Lift from KIKI

	const incrementalRevenue = (revenue * (lift / 100));
	const kikiFee = incrementalRevenue * 0.20; // 20% Success Fee
	const clientNetGain = incrementalRevenue - kikiFee;

	return (
		<div className="p-8 bg-slate-900 border-2 border-emerald-500 rounded-2xl shadow-2xl">
			<h3 className="text-xl font-bold text-white mb-6">Estimate Your OaaS Growth</h3>
			<div className="space-y-6">
				<label className="block text-slate-300">Monthly Revenue: ${revenue.toLocaleString()}</label>
				<input type="range" min="10000" max="1000000" step="10000"
							 value={revenue} onChange={(e) => setRevenue(Number(e.target.value))}
							 className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-emerald-500" />
				<div className="grid grid-cols-2 gap-4 mt-8">
					<div className="p-4 bg-slate-800 rounded-lg">
						<p className="text-xs text-slate-400 uppercase">KIKI Success Fee (20% of Lift)</p>
						<p className="text-2xl font-bold text-emerald-400">${kikiFee.toLocaleString()}</p>
					</div>
					<div className="p-4 bg-emerald-500/10 border border-emerald-500/50 rounded-lg">
						<p className="text-xs text-emerald-400 uppercase font-bold">Your New Net Profit</p>
						<p className="text-2xl font-bold text-white">${clientNetGain.toLocaleString()}</p>
					</div>
				</div>
			</div>
			<p className="mt-6 text-center text-xs text-slate-500">
				*Based on average 2026 performance data from the Council of Nine. Zero upfront cost.
			</p>
		</div>
	);
};

export default OaasCalculator;
