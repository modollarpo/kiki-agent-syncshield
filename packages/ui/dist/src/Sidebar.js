"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Sidebar = void 0;
const jsx_runtime_1 = require("react/jsx-runtime");
/**
 * Enterprise Sidebar — High-Trust, Dark-Mode, Emerald Accents
 */
const Sidebar = ({ items, className = "" }) => ((0, jsx_runtime_1.jsxs)("aside", { className: `w-64 bg-slate-950 border-r border-emerald-500/20 min-h-screen flex flex-col shadow-2xl ${className}`, children: [(0, jsx_runtime_1.jsx)("div", { className: "p-6 text-2xl font-bold text-emerald-400 tracking-tight font-sans border-b border-emerald-500/10", children: "KIKI Agent\u2122" }), (0, jsx_runtime_1.jsx)("nav", { className: "flex-1 p-4 space-y-2", children: items.map((item, i) => ((0, jsx_runtime_1.jsxs)("button", { className: `w-full flex items-center gap-3 px-4 py-3 rounded-lg font-semibold text-left transition
            ${item.active ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/40' :
                    'text-slate-300 hover:bg-slate-800/60'}
          `, onClick: item.onClick, children: [item.icon && (0, jsx_runtime_1.jsx)("span", { className: "text-xl", children: item.icon }), item.label] }, item.label))) }), (0, jsx_runtime_1.jsx)("div", { className: "p-4 text-xs text-slate-500 border-t border-emerald-500/10", children: "\u00A9 2026 KIKI Agent\u2122" })] }));
exports.Sidebar = Sidebar;
exports.default = exports.Sidebar;
