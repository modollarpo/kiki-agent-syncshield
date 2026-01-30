"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.Stepper = void 0;
const jsx_runtime_1 = require("react/jsx-runtime");
const react_1 = __importDefault(require("react"));
const theme_1 = require("../theme");
const Stepper = ({ steps, current }) => ((0, jsx_runtime_1.jsx)("div", { style: { display: 'flex', alignItems: 'center', gap: theme_1.spacing.lg }, children: steps.map((step, i) => ((0, jsx_runtime_1.jsxs)(react_1.default.Fragment, { children: [(0, jsx_runtime_1.jsxs)("div", { style: { display: 'flex', flexDirection: 'column', alignItems: 'center' }, children: [(0, jsx_runtime_1.jsx)("div", { style: {
                            width: 28,
                            height: 28,
                            borderRadius: '50%',
                            background: i < current ? theme_1.colors.success : i === current ? theme_1.colors.primary[500] : theme_1.colors.neutral[300],
                            color: '#fff',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontWeight: 700,
                            fontSize: 16,
                            marginBottom: 4,
                        }, children: i + 1 }), (0, jsx_runtime_1.jsx)("span", { style: { fontSize: 13, color: theme_1.colors.neutral[600], textAlign: 'center' }, children: step.label })] }), i < steps.length - 1 && ((0, jsx_runtime_1.jsx)("div", { style: { flex: 1, height: 2, background: theme_1.colors.neutral[300] } }))] }, step.label))) }));
exports.Stepper = Stepper;
