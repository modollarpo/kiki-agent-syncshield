"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Loader = void 0;
const jsx_runtime_1 = require("react/jsx-runtime");
/**
 * Enterprise Loader — High-Trust, Dark-Mode, Emerald Accents
 */
const Loader = ({ size = 32, color = "#10b981", className = "" }) => ((0, jsx_runtime_1.jsxs)("svg", { className: `animate-spin ${className}`, width: size, height: size, viewBox: "0 0 50 50", fill: "none", xmlns: "http://www.w3.org/2000/svg", role: "status", "aria-label": "Loading", children: [(0, jsx_runtime_1.jsx)("circle", { cx: "25", cy: "25", r: "20", stroke: "#334155", strokeWidth: "6", fill: "none" }), (0, jsx_runtime_1.jsx)("path", { d: "M45 25a20 20 0 1 1-40 0", stroke: color, strokeWidth: "6", strokeLinecap: "round", fill: "none" })] }));
exports.Loader = Loader;
exports.default = exports.Loader;
