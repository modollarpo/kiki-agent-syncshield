"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Input = void 0;
const jsx_runtime_1 = require("react/jsx-runtime");
const theme_1 = require("../theme");
const Input = ({ label, error, style, ...props }) => ((0, jsx_runtime_1.jsxs)("div", { style: { marginBottom: theme_1.spacing.md }, children: [label && ((0, jsx_runtime_1.jsx)("label", { style: {
                display: 'block',
                marginBottom: 4,
                fontWeight: theme_1.typography.headings.fontWeight,
                color: theme_1.colors.neutral[600],
            }, children: label })), (0, jsx_runtime_1.jsx)("input", { style: {
                width: '100%',
                padding: `${theme_1.spacing.sm}px ${theme_1.spacing.md}px`,
                borderRadius: theme_1.radii.sm,
                border: `1px solid ${error ? theme_1.colors.error : theme_1.colors.neutral[300]}`,
                fontFamily: theme_1.typography.fontFamily,
                fontSize: 16,
                outline: 'none',
                boxSizing: 'border-box',
            }, ...props }), error && (0, jsx_runtime_1.jsx)("div", { style: { color: theme_1.colors.error, fontSize: 12 }, children: error })] }));
exports.Input = Input;
