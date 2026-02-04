"use client";

import React, { useEffect, useState } from "react";

export type OaasCalculatorProps = {
	confirmed?: boolean;
	onConfirmedChange?: (confirmed: boolean) => void;
	onConfirm?: () => void;
	storageKey?: string;
	persist?: boolean;
	className?: string;
};

export const OaasCalculator: React.FC<OaasCalculatorProps> = ({
	confirmed,
	onConfirmedChange,
	onConfirm,
	storageKey = "kiki:oaasCalculator",
	persist = true,
	className = "",
}) => {
	const [revenue, setRevenue] = useState(100000); // Current Revenue
	const [lift, setLift] = useState(20); // Expected % Lift from KIKI
	const [internalConfirmed, setInternalConfirmed] = useState(false);

	const isConfirmed = confirmed ?? internalConfirmed;

	useEffect(() => {
		onConfirmedChange?.(isConfirmed);
	}, [isConfirmed, onConfirmedChange]);

	const setConfirmed = (value: boolean) => {
		if (confirmed === undefined) setInternalConfirmed(value);
		onConfirmedChange?.(value);
	};

	useEffect(() => {
		if (!persist) return;
		if (typeof window === "undefined") return;
		try {
			const raw = window.localStorage.getItem(storageKey);
			if (!raw) return;
			const parsed = JSON.parse(raw) as Partial<{
				revenue: number;
				lift: number;
				confirmed: boolean;
			}>;
			if (typeof parsed.revenue === "number" && Number.isFinite(parsed.revenue)) {
				setRevenue(parsed.revenue);
			}
			if (typeof parsed.lift === "number" && Number.isFinite(parsed.lift)) {
				setLift(parsed.lift);
			}
			if (confirmed === undefined && typeof parsed.confirmed === "boolean") {
				setInternalConfirmed(parsed.confirmed);
			}
		} catch {
			// ignore
		}
		// eslint-disable-next-line react-hooks/exhaustive-deps
	}, [persist, storageKey]);

	useEffect(() => {
		if (!persist) return;
		if (typeof window === "undefined") return;
		try {
			window.localStorage.setItem(
				storageKey,
				JSON.stringify({ revenue, lift, confirmed: isConfirmed })
			);
		} catch {
			// ignore
		}
	}, [revenue, lift, isConfirmed, persist, storageKey]);

	const incrementalRevenue = (revenue * (lift / 100));
	const kikiFee = incrementalRevenue * 0.20; // 20% Success Fee
	const clientNetGain = incrementalRevenue - kikiFee;

	return (
		<div className={"p-8 bg-slate-900 border-2 border-emerald-500 rounded-2xl shadow-2xl " + className}>
			<h3 className="text-xl font-bold text-white mb-6">Estimate Your OaaS Growth</h3>
			<div className="space-y-6">
				<label className="block text-slate-300">Monthly Revenue: ${revenue.toLocaleString()}</label>
				<input type="range" min="10000" max="1000000" step="10000"
							 value={revenue} onChange={(e) => setRevenue(Number(e.target.value))}
							 className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-emerald-500" />
				<label className="block text-slate-300">Expected Lift: {lift}%</label>
				<input
					type="range"
					min="1"
					max="60"
					step="1"
					value={lift}
					onChange={(e) => setLift(Number(e.target.value))}
					className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-emerald-500"
				/>
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

			<div className="mt-6 rounded-xl border border-slate-800 bg-slate-950/40 p-4">
				<div className="flex items-start gap-3">
					<input
						type="checkbox"
						id="oaas-confirm"
						className="mt-1"
						checked={isConfirmed}
						onChange={(e) => setConfirmed(e.target.checked)}
					/>
					<label htmlFor="oaas-confirm" className="text-sm text-slate-300">
						I understand these are estimates and the KIKI fee is 20% of incremental lift.
					</label>
				</div>
				<button
					type="button"
					disabled={!isConfirmed}
					onClick={() => {
						if (!isConfirmed) return;
						onConfirm?.();
					}}
					className="mt-4 w-full rounded-lg bg-emerald-600 px-4 py-3 text-sm font-semibold text-white hover:bg-emerald-700 disabled:opacity-40"
				>
					Confirm forecast
				</button>
			</div>
			<p className="mt-6 text-center text-xs text-slate-500">
				*Based on average 2026 performance data from the Council of Nine. Zero upfront cost.
			</p>
		</div>
	);
};

export default OaasCalculator;
