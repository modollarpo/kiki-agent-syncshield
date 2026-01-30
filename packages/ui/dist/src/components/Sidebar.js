"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Sidebar = void 0;
const jsx_runtime_1 = require("react/jsx-runtime");
const theme_1 = require("../theme");
const Sidebar = ({ items, logo, footer, style }) => ((0, jsx_runtime_1.jsxs)("aside", { style: {
        width: 260,
        background: 'var(--sidebar-bg, ' + theme_1.colors.neutral[600] + ')',
        color: theme_1.colors.neutral[100],
        display: 'flex',
        flexDirection: 'column',
        minHeight: '100vh',
        borderRight: `1px solid ${theme_1.colors.neutral[400]}`,
        ...style,
    }, children: [(0, jsx_runtime_1.jsx)("div", { style: { padding: theme_1.spacing.lg, fontWeight: theme_1.typography.headings.fontWeight, fontSize: 22 }, children: logo || 'KIKI Agent™' }), (0, jsx_runtime_1.jsx)("nav", { style: { flex: 1 }, children: items.map((item, i) => ((0, jsx_runtime_1.jsxs)("div", { onClick: item.onClick, style: {
                    display: 'flex',
                    alignItems: 'center',
                    padding: `${theme_1.spacing.md}px ${theme_1.spacing.lg}px`,
                    background: item.active ? theme_1.colors.primary[500] : 'transparent',
                    color: item.active ? '#fff' : theme_1.colors.neutral[100],
                    borderRadius: theme_1.radii.md,
                    margin: '4px 8px',
                    cursor: 'pointer',
                    fontWeight: item.active ? 700 : 500,
                    fontSize: 16,
                    transition: 'background 0.2s',
                }, children: [item.icon && (0, jsx_runtime_1.jsx)("span", { style: { marginRight: 12 }, children: item.icon }), item.label] }, item.label))) }), footer && (0, jsx_runtime_1.jsx)("div", { style: { padding: theme_1.spacing.lg, fontSize: 13, color: theme_1.colors.neutral[400] }, children: footer })] }));
exports.Sidebar = Sidebar;
