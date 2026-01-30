"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Default = void 0;
const jsx_runtime_1 = require("react/jsx-runtime");
const react_1 = require("react");
const Modal_1 = require("../Modal");
const meta = {
    title: 'Enterprise/Modal',
    component: Modal_1.Modal,
    tags: ['autodocs'],
    parameters: {
        layout: 'centered',
    },
};
exports.default = meta;
exports.Default = {
    render: (args) => {
        const [open, setOpen] = (0, react_1.useState)(true);
        return ((0, jsx_runtime_1.jsxs)(jsx_runtime_1.Fragment, { children: [(0, jsx_runtime_1.jsx)("button", { className: "px-4 py-2 bg-emerald-600 text-white rounded-lg font-semibold mb-4", onClick: () => setOpen(true), children: "Open Modal" }), (0, jsx_runtime_1.jsx)(Modal_1.Modal, { ...args, open: open, onClose: () => setOpen(false), children: (0, jsx_runtime_1.jsxs)("p", { children: ["This is a high-trust, enterprise modal.", (0, jsx_runtime_1.jsx)("br", {}), "Use for critical confirmations, onboarding, or secure workflows."] }) })] }));
    },
    args: {
        title: 'Enterprise Modal',
    },
};
