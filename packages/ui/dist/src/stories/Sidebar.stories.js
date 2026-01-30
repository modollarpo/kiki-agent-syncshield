"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.WithCustomFooter = exports.Default = void 0;
const jsx_runtime_1 = require("react/jsx-runtime");
const index_1 = require("../index");
const meta = {
    title: "Components/Sidebar",
    component: index_1.Sidebar,
    tags: ["autodocs"],
    parameters: {
        layout: "fullscreen",
        backgrounds: { default: "dark" },
    },
};
exports.default = meta;
exports.Default = {
    args: {
        items: [
            { label: "Dashboard", icon: "🏠", active: true },
            { label: "Agents", icon: "🤖" },
            { label: "Billing", icon: "💳" },
            { label: "Settings", icon: "⚙️" },
        ],
        logo: "KIKI Agent™",
        footer: "© 2024 KIKI Agent™",
    },
};
exports.WithCustomFooter = {
    args: {
        items: [
            { label: "Dashboard", icon: "🏠" },
            { label: "Agents", icon: "🤖", active: true },
            { label: "Billing", icon: "💳" },
            { label: "Settings", icon: "⚙️" },
        ],
        logo: (0, jsx_runtime_1.jsx)("span", { style: { fontWeight: 700 }, children: "KIKI Agent\u2122" }),
        footer: (0, jsx_runtime_1.jsx)("div", { style: { fontSize: 12 }, children: "Custom Footer Content" }),
    },
};
