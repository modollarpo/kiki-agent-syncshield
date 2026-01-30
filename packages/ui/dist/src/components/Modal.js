"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Modal = void 0;
const jsx_runtime_1 = require("react/jsx-runtime");
const theme_1 = require("../theme");
const Modal = ({ open, onClose, title, children }) => {
    if (!open)
        return null;
    return ((0, jsx_runtime_1.jsx)("div", { style: {
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100vw',
            height: '100vh',
            background: 'rgba(0,0,0,0.4)',
            zIndex: 1000,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
        }, "aria-modal": "true", role: "dialog", tabIndex: -1, onClick: onClose, children: (0, jsx_runtime_1.jsxs)("div", { style: {
                background: 'var(--modal-bg, #fff)',
                borderRadius: theme_1.radii.lg,
                boxShadow: theme_1.shadows.lg,
                minWidth: 400,
                maxWidth: '90vw',
                padding: 32,
                position: 'relative',
            }, onClick: e => e.stopPropagation(), children: [title && (0, jsx_runtime_1.jsx)("h2", { style: { marginTop: 0 }, children: title }), children, (0, jsx_runtime_1.jsx)("button", { "aria-label": "Close", onClick: onClose, style: {
                        position: 'absolute',
                        top: 16,
                        right: 16,
                        background: 'none',
                        border: 'none',
                        fontSize: 24,
                        cursor: 'pointer',
                    }, children: "\u00D7" })] }) }));
};
exports.Modal = Modal;
