"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Notification = void 0;
const jsx_runtime_1 = require("react/jsx-runtime");
const theme_1 = require("../theme");
const typeMap = {
    info: theme_1.colors.info,
    success: theme_1.colors.success,
    warning: theme_1.colors.warning,
    error: theme_1.colors.error,
};
const Notification = ({ message, type = 'info', onClose }) => ((0, jsx_runtime_1.jsxs)("div", { style: {
        background: typeMap[type],
        color: '#fff',
        borderRadius: theme_1.radii.md,
        boxShadow: theme_1.shadows.md,
        padding: `${theme_1.spacing.md}px ${theme_1.spacing.lg}px`,
        display: 'flex',
        alignItems: 'center',
        marginBottom: theme_1.spacing.md,
        position: 'relative',
        minWidth: 320,
        maxWidth: 480,
    }, role: "alert", children: [(0, jsx_runtime_1.jsx)("span", { style: { flex: 1 }, children: message }), onClose && ((0, jsx_runtime_1.jsx)("button", { onClick: onClose, "aria-label": "Close notification", style: {
                background: 'none',
                border: 'none',
                color: '#fff',
                fontSize: 18,
                marginLeft: theme_1.spacing.md,
                cursor: 'pointer',
            }, children: "\u00D7" }))] }));
exports.Notification = Notification;
