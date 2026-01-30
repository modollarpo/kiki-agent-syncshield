"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.OnboardingChecklist = void 0;
const jsx_runtime_1 = require("react/jsx-runtime");
const checklistItems = [
    { id: 1, task: "Connect Marketing APIs", status: "PENDING", desc: "Link Google/Meta via OAuth" },
    { id: 2, task: "Historical Data Ingest", status: "WAITING", desc: "Syncing Stripe/Shopify for LTV modeling" },
    { id: 3, task: "Brand Identity Upload", status: "PENDING", desc: "Upload logos and color palettes for SyncCreate" },
    { id: 4, task: "Budget Authorization", status: "LOCKED", desc: "Approve KIKI's proposed daily spend" }
];
const OnboardingChecklist = () => {
    return ((0, jsx_runtime_1.jsxs)("div", { className: "bg-slate-900 p-8 rounded-xl border border-emerald-500/30", children: [(0, jsx_runtime_1.jsx)("h2", { className: "text-2xl font-bold text-white mb-4", children: "Initialize Your Revenue Engine" }), checklistItems.map(item => ((0, jsx_runtime_1.jsxs)("div", { className: "flex items-center justify-between py-3 border-b border-slate-800", children: [(0, jsx_runtime_1.jsxs)("div", { children: [(0, jsx_runtime_1.jsx)("p", { className: "text-emerald-400 font-semibold", children: item.task }), (0, jsx_runtime_1.jsx)("p", { className: "text-slate-400 text-sm", children: item.desc })] }), (0, jsx_runtime_1.jsx)("button", { className: "px-4 py-2 bg-emerald-600 rounded-lg text-white", children: "Connect" })] }, item.id)))] }));
};
exports.OnboardingChecklist = OnboardingChecklist;
exports.default = exports.OnboardingChecklist;
