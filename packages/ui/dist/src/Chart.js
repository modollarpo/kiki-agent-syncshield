"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Chart = void 0;
const jsx_runtime_1 = require("react/jsx-runtime");
/**
 * Enterprise Chart — High-Trust, Dark-Mode, Emerald Accents
 * Simple bar chart for quick metrics visualization.
 */
const Chart = ({ title, data, className = "" }) => {
    const max = Math.max(...data.map(d => d.value), 1);
    return ((0, jsx_runtime_1.jsxs)("div", { className: `bg-slate-900 border border-emerald-500/30 rounded-2xl p-6 shadow-xl ${className}`, children: [title && (0, jsx_runtime_1.jsx)("h3", { className: "text-lg font-bold text-emerald-400 mb-4 font-sans", children: title }), (0, jsx_runtime_1.jsx)("div", { className: "space-y-3", children: data.map((d, i) => ((0, jsx_runtime_1.jsxs)("div", { className: "flex items-center gap-4", children: [(0, jsx_runtime_1.jsx)("span", { className: "w-24 text-slate-300 font-mono text-xs", children: d.label }), (0, jsx_runtime_1.jsx)("div", { className: "flex-1 h-4 bg-slate-800 rounded-lg overflow-hidden", children: (0, jsx_runtime_1.jsx)("div", { className: "h-4 bg-gradient-to-r from-emerald-500 to-emerald-300 rounded-lg transition-all", style: { width: `${(d.value / max) * 100}%` } }) }), (0, jsx_runtime_1.jsx)("span", { className: "w-12 text-right text-emerald-400 font-bold font-mono", children: d.value })] }, d.label))) })] }));
};
exports.Chart = Chart;
exports.default = exports.Chart;
