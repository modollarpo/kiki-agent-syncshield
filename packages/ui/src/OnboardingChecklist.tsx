import React from "react";

export type ChecklistItem = {
	id: number;
	task: string;
	status: "PENDING" | "WAITING" | "LOCKED" | "COMPLETE";
	desc: string;
};

const checklistItems: ChecklistItem[] = [
	{ id: 1, task: "Connect Marketing APIs", status: "PENDING", desc: "Link Google/Meta via OAuth" },
	{ id: 2, task: "Historical Data Ingest", status: "WAITING", desc: "Syncing Stripe/Shopify for LTV modeling" },
	{ id: 3, task: "Brand Identity Upload", status: "PENDING", desc: "Upload logos and color palettes for SyncCreate" },
	{ id: 4, task: "Budget Authorization", status: "LOCKED", desc: "Approve KIKI's proposed daily spend" }
];

export const OnboardingChecklist: React.FC = () => {
	return (
		<div className="bg-slate-900 p-8 rounded-xl border border-emerald-500/30">
			<h2 className="text-2xl font-bold text-white mb-4">Initialize Your Revenue Engine</h2>
			{checklistItems.map(item => (
				<div key={item.id} className="flex items-center justify-between py-3 border-b border-slate-800">
					 <div>
						 <p className="text-emerald-400 font-semibold">{item.task}</p>
						 <p className="text-slate-400 text-sm">{item.desc}</p>
					 </div>
					 <button className="px-4 py-2 bg-emerald-600 rounded-lg text-white">Connect</button>
				</div>
			))}
		</div>
	);
}

export default OnboardingChecklist;
