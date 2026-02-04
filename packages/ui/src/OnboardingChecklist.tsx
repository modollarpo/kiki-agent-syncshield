"use client";

import React, { useEffect, useMemo, useState } from "react";

export type ChecklistItem = {
	id: number;
	task: string;
	status: "PENDING" | "WAITING" | "LOCKED" | "COMPLETE";
	desc: string;
};

const seedChecklistItems: ChecklistItem[] = [
	{ id: 1, task: "Connect Marketing APIs", status: "PENDING", desc: "Link Google/Meta via OAuth" },
	{ id: 2, task: "Historical Data Ingest", status: "WAITING", desc: "Syncing Stripe/Shopify for LTV modeling" },
	{ id: 3, task: "Brand Identity Upload", status: "PENDING", desc: "Upload logos and color palettes for SyncCreate" },
	{ id: 4, task: "Budget Authorization", status: "LOCKED", desc: "Approve KIKI's proposed daily spend" }
];

export type OnboardingChecklistProps = {
	onCompletionChange?: (isComplete: boolean) => void;
	requiredItemIds?: number[];
	storageKey?: string;
	persist?: boolean;
	className?: string;
};

function statusBadge(status: ChecklistItem["status"]) {
	switch (status) {
		case "COMPLETE":
			return "bg-emerald-500/15 text-emerald-300 border-emerald-500/30";
		case "PENDING":
			return "bg-slate-700/30 text-slate-200 border-slate-600/40";
		case "WAITING":
			return "bg-amber-500/10 text-amber-200 border-amber-500/20";
		case "LOCKED":
		default:
			return "bg-slate-800/60 text-slate-400 border-slate-700/60";
	}
}

function actionLabel(status: ChecklistItem["status"]) {
	switch (status) {
		case "COMPLETE":
			return "Connected";
		case "WAITING":
			return "Resume";
		case "LOCKED":
			return "Locked";
		case "PENDING":
		default:
			return "Connect";
	}
}

export const OnboardingChecklist: React.FC<OnboardingChecklistProps> = ({
	onCompletionChange,
	requiredItemIds = [1, 3, 4],
	storageKey = "kiki:onboardingChecklist",
	persist = true,
	className = "",
}) => {
	const [items, setItems] = useState<ChecklistItem[]>(seedChecklistItems);

	useEffect(() => {
		if (!persist) return;
		if (typeof window === "undefined") return;
		try {
			const raw = window.localStorage.getItem(storageKey);
			if (!raw) return;
			const parsed = JSON.parse(raw) as ChecklistItem[];
			if (!Array.isArray(parsed)) return;
			// Minimal validation: ensure required fields exist.
			const normalized = parsed
				.filter((x) => x && typeof x.id === "number" && typeof x.status === "string")
				.map((x) => ({
					id: x.id,
					task: String((x as any).task ?? ""),
					desc: String((x as any).desc ?? ""),
					status: (x as any).status as ChecklistItem["status"],
				}))
				.sort((a, b) => a.id - b.id);
			if (normalized.length) setItems(normalized);
		} catch {
			// ignore
		}
	}, [persist, storageKey]);

	useEffect(() => {
		if (!persist) return;
		if (typeof window === "undefined") return;
		try {
			window.localStorage.setItem(storageKey, JSON.stringify(items));
		} catch {
			// ignore
		}
	}, [items, persist, storageKey]);

	const requiredSet = useMemo(() => new Set(requiredItemIds), [requiredItemIds]);
	const isComplete = useMemo(() => {
		const byId = new Map(items.map((i) => [i.id, i] as const));
		for (const id of requiredSet) {
			const item = byId.get(id);
			if (!item || item.status !== "COMPLETE") return false;
		}
		return true;
	}, [items, requiredSet]);

	useEffect(() => {
		onCompletionChange?.(isComplete);
	}, [isComplete, onCompletionChange]);

	const connect = (id: number) => {
		setItems((prev) => {
			const next: ChecklistItem[] = prev.map((item): ChecklistItem => {
				if (item.id !== id) return item;
				if (item.status === "LOCKED") return item;
				return { ...item, status: "COMPLETE" };
			});

			const byId: Map<number, ChecklistItem> = new Map(next.map((i) => [i.id, i] as const));
			const marketingDone = byId.get(1)?.status === "COMPLETE";
			const brandDone = byId.get(3)?.status === "COMPLETE";
			const ingest = byId.get(2);
			const budget = byId.get(4);

			// Unlock ingest once marketing is connected.
			if (ingest && marketingDone && ingest.status === "WAITING") {
				byId.set(2, { ...ingest, status: "PENDING" });
			}
			// Unlock budget once marketing + brand are completed.
			if (budget && marketingDone && brandDone && budget.status === "LOCKED") {
				byId.set(4, { ...budget, status: "PENDING" });
			}

			return Array.from(byId.values()).sort((a, b) => a.id - b.id);
		});
	};

	return (
		<div className={"bg-slate-900 p-8 rounded-xl border border-emerald-500/30 " + className}>
			<h2 className="text-2xl font-bold text-white mb-4">Initialize Your Revenue Engine</h2>
			{items.map((item) => (
				<div key={item.id} className="flex items-center justify-between py-3 border-b border-slate-800">
					 <div className="pr-3">
						 <p className="text-emerald-400 font-semibold">{item.task}</p>
						 <p className="text-slate-400 text-sm">{item.desc}</p>
					 </div>
					 <div className="flex items-center gap-2">
						<span
							className={
								"rounded-full border px-2 py-1 text-[11px] uppercase tracking-wide " +
								statusBadge(item.status)
							}
						>
							{item.status}
						</span>
						<button
							type="button"
							onClick={() => connect(item.id)}
							disabled={item.status === "LOCKED" || item.status === "COMPLETE"}
							className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-40 rounded-lg text-white"
						>
							{actionLabel(item.status)}
						</button>
					 </div>
				</div>
			))}
			<div className="mt-4 text-xs text-slate-400">
				Required to proceed: connect marketing, upload brand identity, authorize budget.
			</div>
		</div>
	);
}

export default OnboardingChecklist;
