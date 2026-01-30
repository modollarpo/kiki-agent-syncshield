"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Button = void 0;
const jsx_runtime_1 = require("react/jsx-runtime");
const theme_1 = require("../theme");
const sizeMap = {
    sm: { padding: `${theme_1.spacing.sm}px ${theme_1.spacing.md}px`, fontSize: 14 },
    md: { padding: `${theme_1.spacing.md}px ${theme_1.spacing.lg}px`, fontSize: 16 },
    lg: { padding: `${theme_1.spacing.lg}px ${theme_1.spacing.xl}px`, fontSize: 18 },
};
const Button = ({ children, variant = 'primary', size = 'md', style, ...props }) => {
    let bg, color, border;
    switch (variant) {
        case 'primary':
            bg = theme_1.colors.primary[500];
            color = '#fff';
            border = 'none';
            break;
        case 'secondary':
            bg = theme_1.colors.secondary[500];
            color = '#fff';
            border = 'none';
            break;
        case 'danger':
            bg = theme_1.colors.error;
            color = '#fff';
            border = 'none';
            break;
        case 'ghost':
            bg = 'transparent';
            color = theme_1.colors.primary[500];
            border = `1px solid ${theme_1.colors.primary[500]}`;
            break;
        default:
            bg = theme_1.colors.primary[500];
            color = '#fff';
            border = 'none';
    }
    const { padding, fontSize } = sizeMap[size];
    return ((0, jsx_runtime_1.jsx)("button", { style: {
            background: bg,
            color,
            border,
            borderRadius: theme_1.radii.md,
            fontFamily: theme_1.typography.fontFamily,
            fontWeight: theme_1.typography.headings.fontWeight,
            fontSize,
            padding,
            cursor: 'pointer',
            transition: 'background 0.2s',
            ...style,
        }, ...props, children: children }));
};
exports.Button = Button;
