"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Loader = void 0;
const jsx_runtime_1 = require("react/jsx-runtime");
const theme_1 = require("../theme");
const Loader = ({ size = 32, color }) => ((0, jsx_runtime_1.jsx)("svg", { width: size, height: size, viewBox: "0 0 50 50", style: { display: 'block', margin: 'auto' }, "aria-label": "Loading", children: (0, jsx_runtime_1.jsx)("circle", { cx: "25", cy: "25", r: "20", fill: "none", stroke: color || theme_1.colors.primary[500], strokeWidth: "5", strokeDasharray: "31.4 31.4", strokeLinecap: "round", transform: "rotate(-90 25 25)", children: (0, jsx_runtime_1.jsx)("animateTransform", { attributeName: "transform", type: "rotate", from: "0 25 25", to: "360 25 25", dur: "1s", repeatCount: "indefinite" }) }) }));
exports.Loader = Loader;
