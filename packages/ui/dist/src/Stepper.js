"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Stepper = void 0;
const jsx_runtime_1 = require("react/jsx-runtime");
/**
 * Enterprise Stepper — High-Trust, Dark-Mode, Emerald Accents
 */
const Stepper = ({ steps, className = "" }) => ((0, jsx_runtime_1.jsx)("nav", { className: `flex flex-col gap-4 bg-slate-900 p-6 rounded-2xl border border-emerald-500/30 shadow-xl ${className}`, "aria-label": "Progress", children: (0, jsx_runtime_1.jsx)("ol", { className: "flex flex-col gap-2", children: steps.map((step, i) => ((0, jsx_runtime_1.jsxs)("li", { className: "flex items-center gap-4", children: [(0, jsx_runtime_1.jsx)("span", { className: `flex items-center justify-center w-8 h-8 rounded-full border-2 font-bold text-lg transition-all
              ${step.completed ? 'bg-emerald-500 border-emerald-500 text-slate-900' :
                        step.current ? 'border-emerald-400 text-emerald-400' :
                            'border-slate-700 text-slate-500 bg-slate-800'}`, children: step.completed ? '✓' : i + 1 }), (0, jsx_runtime_1.jsxs)("div", { className: "flex flex-col", children: [(0, jsx_runtime_1.jsx)("span", { className: `font-semibold ${step.current ? 'text-emerald-400' : 'text-slate-200'}`, children: step.label }), step.description && (0, jsx_runtime_1.jsx)("span", { className: "text-xs text-slate-400", children: step.description })] })] }, i))) }) }));
exports.Stepper = Stepper;
exports.default = exports.Stepper;
