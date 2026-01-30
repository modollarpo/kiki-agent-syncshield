"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.LegalConsent = void 0;
const jsx_runtime_1 = require("react/jsx-runtime");
const LegalConsent = () => {
    return ((0, jsx_runtime_1.jsxs)("div", { className: "space-y-4 p-6 bg-slate-800 rounded-lg", children: [(0, jsx_runtime_1.jsxs)("div", { className: "flex items-start gap-3", children: [(0, jsx_runtime_1.jsx)("input", { type: "checkbox", id: "terms", className: "mt-1" }), (0, jsx_runtime_1.jsxs)("label", { htmlFor: "terms", className: "text-sm text-slate-300", children: ["I authorize KIKI to manage my ad spend and generate creative assets based on the ", (0, jsx_runtime_1.jsx)("b", { children: "Risk Appetite" }), " I have configured."] })] }), (0, jsx_runtime_1.jsxs)("div", { className: "flex items-start gap-3", children: [(0, jsx_runtime_1.jsx)("input", { type: "checkbox", id: "privacy", className: "mt-1" }), (0, jsx_runtime_1.jsxs)("label", { htmlFor: "privacy", className: "text-sm text-slate-300", children: ["I understand that my data will be processed by 9 autonomous agents to optimize LTV, as described in the ", (0, jsx_runtime_1.jsx)("b", { children: "Privacy Policy" }), "."] })] }), (0, jsx_runtime_1.jsx)("button", { className: "w-full py-3 bg-emerald-500 hover:bg-emerald-600 text-white font-bold rounded-lg transition-all", children: "Finalize & Deploy Council of Nine" })] }));
};
exports.LegalConsent = LegalConsent;
exports.default = exports.LegalConsent;
