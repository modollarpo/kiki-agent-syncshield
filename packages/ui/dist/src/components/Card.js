"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Card = void 0;
const jsx_runtime_1 = require("react/jsx-runtime");
const theme_1 = require("../theme");
// Add index signature to shadows for TS
const _shadows = theme_1.shadows;
const Card = ({ children, elevation = 'md', style, ...props }) => ((0, jsx_runtime_1.jsx)("div", { style: {
        borderRadius: theme_1.radii.lg,
        boxShadow: _shadows[elevation],
        background: 'var(--card-bg, #fff)',
        padding: 24,
        ...style,
    }, ...props, children: children }));
exports.Card = Card;
