"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Notification = void 0;
const jsx_runtime_1 = require("react/jsx-runtime");
const typeStyles = {
    success: "bg-emerald-900 border-emerald-500 text-emerald-300",
    error: "bg-red-900 border-red-500 text-red-300",
    warning: "bg-yellow-900 border-yellow-500 text-yellow-300",
    info: "bg-slate-800 border-slate-500 text-slate-200",
};
const Notification = ({ type = "info", title, message, onClose, className = "", }) => ((0, jsx_runtime_1.jsxs)("div", { className: `relative rounded-xl border shadow-lg px-6 py-4 flex items-start gap-4 ${typeStyles[type]} ${className}`, role: "alert", children: [(0, jsx_runtime_1.jsxs)("div", { className: "flex-1", children: [title && (0, jsx_runtime_1.jsx)("div", { className: "font-bold text-lg mb-1 font-sans", children: title }), (0, jsx_runtime_1.jsx)("div", { className: "text-base font-sans", children: message })] }), onClose && ((0, jsx_runtime_1.jsx)("button", { className: "absolute top-2 right-2 text-xl text-emerald-400 hover:text-emerald-200 focus:outline-none", onClick: onClose, "aria-label": "Close notification", children: "\u00D7" }))] }));
exports.Notification = Notification;
exports.default = exports.Notification;
