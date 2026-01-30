import React, { useState } from "react";

interface ImpactAuditResult {
	projected_uplift: number;
	kiki_performance_fee: number;
	client_net_profit: number;
	conservative_uplift: number;
	aggressive_uplift: number;
	prospect_id: string;
}

export const ImpactAuditForm: React.FC<{}> = () => {
	const [monthlyCustomers, setMonthlyCustomers] = useState(1000);
	const [ltv, setLtv] = useState(120.0);
	const [churn, setChurn] = useState(8.0);
	const [result, setResult] = useState<ImpactAuditResult | null>(null);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState<string | null>(null);

	const handleSubmit = async (e: React.FormEvent) => {
		e.preventDefault();
		setLoading(true);
		setError(null);
		setResult(null);
		try {
			const res = await fetch("/api/impact_audit", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					monthly_customers: monthlyCustomers,
					ltv,
					churn,
				}),
			});
			if (!res.ok) throw new Error("API error");
			const data = await res.json();
			setResult(data);
		} catch (err: any) {
			setError(err.message || "Unknown error");
		} finally {
			setLoading(false);
		}
	};

	return (
		<form onSubmit={handleSubmit} className="p-8 bg-slate-900 border-2 border-emerald-500 rounded-2xl shadow-2xl space-y-6">
			<h3 className="text-xl font-bold text-white mb-6">Impact Audit</h3>
			<div className="grid grid-cols-3 gap-6">
				<div>
					<label className="block text-slate-300 mb-2">Monthly Customers</label>
					<input
						type="number"
						value={monthlyCustomers}
						onChange={(e: React.ChangeEvent<HTMLInputElement>) => setMonthlyCustomers(Number(e.target.value))}
						className="w-full p-2 rounded bg-slate-800 text-white"
						min={1}
					/>
				</div>
				<div>
					<label className="block text-slate-300 mb-2">Avg. LTV ($)</label>
					<input
						type="number"
						value={ltv}
						onChange={(e: React.ChangeEvent<HTMLInputElement>) => setLtv(Number(e.target.value))}
						className="w-full p-2 rounded bg-slate-800 text-white"
						min={1}
						step={0.01}
					/>
				</div>
				<div>
					<label className="block text-slate-300 mb-2">Churn Rate (%)</label>
					<input
						type="number"
						value={churn}
						onChange={(e: React.ChangeEvent<HTMLInputElement>) => setChurn(Number(e.target.value))}
						className="w-full p-2 rounded bg-slate-800 text-white"
						min={0}
						max={100}
						step={0.01}
					/>
				</div>
			</div>
			<button
				type="submit"
				className="w-full py-3 bg-emerald-500 hover:bg-emerald-600 text-white font-bold rounded-lg transition-all"
				disabled={loading}
			>
				{loading ? "Calculating..." : "Run Audit"}
			</button>
			{error && <p className="text-red-500 text-center">{error}</p>}
			{result && (
				<div className="mt-8 bg-slate-800 p-6 rounded-lg">
					<h4 className="text-lg font-bold text-emerald-400 mb-2">Audit Results</h4>
					<ul className="text-slate-300 space-y-1">
						<li>Projected Uplift: <b>{result.projected_uplift.toLocaleString()}</b></li>
						<li>KIKI Performance Fee: <b>{result.kiki_performance_fee.toLocaleString()}</b></li>
						<li>Client Net Profit: <b>{result.client_net_profit.toLocaleString()}</b></li>
						<li>Conservative Uplift: <b>{result.conservative_uplift.toLocaleString()}</b></li>
						<li>Aggressive Uplift: <b>{result.aggressive_uplift.toLocaleString()}</b></li>
						<li>Prospect ID: <b>{result.prospect_id}</b></li>
					</ul>
				</div>
			)}
		</form>
	);
}

export default ImpactAuditForm;
