"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Modal = void 0;
const jsx_runtime_1 = require("react/jsx-runtime");
/**
 * Enterprise Modal — High-Trust, Dark-Mode, Emerald Accents
 */
const Modal = ({ open, onClose, title, children }) => {
    if (!open)
        return null;
    return ((0, jsx_runtime_1.jsx)("div", { className: "fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm", children: (0, jsx_runtime_1.jsxs)("div", { className: "bg-slate-900 rounded-2xl shadow-2xl border border-emerald-500/40 w-full max-w-lg p-8 relative", children: [(0, jsx_runtime_1.jsx)("button", { className: "absolute top-4 right-4 text-emerald-400 hover:text-emerald-300 text-2xl font-bold focus:outline-none", onClick: onClose, "aria-label": "Close modal", children: "\u00D7" }), title && (0, jsx_runtime_1.jsx)("h2", { className: "text-2xl font-bold text-emerald-400 mb-4 font-sans tracking-tight", children: title }), (0, jsx_runtime_1.jsx)("div", { className: "text-slate-200 font-sans text-base", children: children })] }) }));
};
exports.Modal = Modal;
exports.default = exports.Modal;
