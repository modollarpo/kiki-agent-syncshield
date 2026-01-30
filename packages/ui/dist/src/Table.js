"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Table = Table;
const jsx_runtime_1 = require("react/jsx-runtime");
/**
 * Enterprise Table — High-Trust, Dark-Mode, Emerald Accents
 */
function Table({ columns, data, className = "" }) {
    return ((0, jsx_runtime_1.jsx)("div", { className: `overflow-x-auto rounded-2xl border border-emerald-500/30 bg-slate-900 shadow-xl ${className}`, children: (0, jsx_runtime_1.jsxs)("table", { className: "min-w-full divide-y divide-slate-800", children: [(0, jsx_runtime_1.jsx)("thead", { className: "bg-slate-950", children: (0, jsx_runtime_1.jsx)("tr", { children: columns.map(col => ((0, jsx_runtime_1.jsx)("th", { className: "px-6 py-4 text-left text-xs font-bold text-emerald-400 uppercase tracking-wider border-b border-emerald-500/20", children: col.label }, String(col.key)))) }) }), (0, jsx_runtime_1.jsx)("tbody", { className: "divide-y divide-slate-800", children: data.length === 0 ? ((0, jsx_runtime_1.jsx)("tr", { children: (0, jsx_runtime_1.jsx)("td", { colSpan: columns.length, className: "px-6 py-8 text-center text-slate-500", children: "No data available" }) })) : (data.map((row, i) => ((0, jsx_runtime_1.jsx)("tr", { className: "hover:bg-slate-800/60 transition", children: columns.map(col => ((0, jsx_runtime_1.jsx)("td", { className: "px-6 py-4 text-slate-200 font-mono", children: col.render ? col.render(row[col.key], row) : row[col.key] }, String(col.key)))) }, i)))) })] }) }));
}
exports.default = Table;
