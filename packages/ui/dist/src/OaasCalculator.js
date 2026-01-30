"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.OaasCalculator = void 0;
const jsx_runtime_1 = require("react/jsx-runtime");
const react_1 = require("react");
const OaasCalculator = () => {
    const [revenue, setRevenue] = (0, react_1.useState)(100000); // Current Revenue
    const [lift, setLift] = (0, react_1.useState)(20); // Expected % Lift from KIKI
    const incrementalRevenue = (revenue * (lift / 100));
    const kikiFee = incrementalRevenue * 0.20; // 20% Success Fee
    const clientNetGain = incrementalRevenue - kikiFee;
    return ((0, jsx_runtime_1.jsxs)("div", { className: "p-8 bg-slate-900 border-2 border-emerald-500 rounded-2xl shadow-2xl", children: [(0, jsx_runtime_1.jsx)("h3", { className: "text-xl font-bold text-white mb-6", children: "Estimate Your OaaS Growth" }), (0, jsx_runtime_1.jsxs)("div", { className: "space-y-6", children: [(0, jsx_runtime_1.jsxs)("label", { className: "block text-slate-300", children: ["Monthly Revenue: $", revenue.toLocaleString()] }), (0, jsx_runtime_1.jsx)("input", { type: "range", min: "10000", max: "1000000", step: "10000", value: revenue, onChange: (e) => setRevenue(Number(e.target.value)), className: "w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-emerald-500" }), (0, jsx_runtime_1.jsxs)("div", { className: "grid grid-cols-2 gap-4 mt-8", children: [(0, jsx_runtime_1.jsxs)("div", { className: "p-4 bg-slate-800 rounded-lg", children: [(0, jsx_runtime_1.jsx)("p", { className: "text-xs text-slate-400 uppercase", children: "KIKI Success Fee (20% of Lift)" }), (0, jsx_runtime_1.jsxs)("p", { className: "text-2xl font-bold text-emerald-400", children: ["$", kikiFee.toLocaleString()] })] }), (0, jsx_runtime_1.jsxs)("div", { className: "p-4 bg-emerald-500/10 border border-emerald-500/50 rounded-lg", children: [(0, jsx_runtime_1.jsx)("p", { className: "text-xs text-emerald-400 uppercase font-bold", children: "Your New Net Profit" }), (0, jsx_runtime_1.jsxs)("p", { className: "text-2xl font-bold text-white", children: ["$", clientNetGain.toLocaleString()] })] })] })] }), (0, jsx_runtime_1.jsx)("p", { className: "mt-6 text-center text-xs text-slate-500", children: "*Based on average 2026 performance data from the Council of Nine. Zero upfront cost." })] }));
};
exports.OaasCalculator = OaasCalculator;
exports.default = exports.OaasCalculator;
