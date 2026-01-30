"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.LTVChart = void 0;
const jsx_runtime_1 = require("react/jsx-runtime");
const theme_1 = require("../theme");
const LTVChart = ({ data, height = 240 }) => {
    // Simple SVG line chart for LTV (production: use recharts, nivo, etc.)
    if (!data.length)
        return (0, jsx_runtime_1.jsx)("div", { style: { height }, children: "No data" });
    const maxLTV = Math.max(...data.map(d => d.ltv));
    const minLTV = Math.min(...data.map(d => d.ltv));
    const points = data.map((d, i) => {
        const x = (i / (data.length - 1)) * 400;
        const y = height - ((d.ltv - minLTV) / (maxLTV - minLTV || 1)) * (height - 40) - 20;
        return `${x},${y}`;
    });
    return ((0, jsx_runtime_1.jsxs)("svg", { width: 420, height: height, style: { background: theme_1.colors.neutral[100], borderRadius: 8 }, children: [(0, jsx_runtime_1.jsx)("polyline", { fill: "none", stroke: theme_1.colors.primary[500], strokeWidth: 3, points: points.join(' ') }), data.map((d, i) => {
                const [x, y] = points[i].split(',').map(Number);
                return ((0, jsx_runtime_1.jsx)("circle", { cx: x, cy: y, r: 4, fill: theme_1.colors.primary[500] }, i));
            }), (0, jsx_runtime_1.jsx)("line", { x1: 20, y1: height - 20, x2: 400, y2: height - 20, stroke: theme_1.colors.neutral[400] }), (0, jsx_runtime_1.jsx)("line", { x1: 20, y1: 20, x2: 20, y2: height - 20, stroke: theme_1.colors.neutral[400] }), (0, jsx_runtime_1.jsx)("text", { x: 10, y: 30, fontSize: 12, fill: theme_1.colors.neutral[600], children: "LTV" }), (0, jsx_runtime_1.jsx)("text", { x: 400, y: height - 5, fontSize: 12, fill: theme_1.colors.neutral[600], children: "Date" })] }));
};
exports.LTVChart = LTVChart;
