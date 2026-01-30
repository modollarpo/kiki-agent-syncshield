"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Avatar = void 0;
const jsx_runtime_1 = require("react/jsx-runtime");
const theme_1 = require("../theme");
const Avatar = ({ src, name, size = 40 }) => {
    const initials = name ? name.split(' ').map(n => n[0]).join('').toUpperCase() : '';
    return src ? ((0, jsx_runtime_1.jsx)("img", { src: src, alt: name || 'Avatar', width: size, height: size, style: {
            borderRadius: '50%',
            objectFit: 'cover',
            width: size,
            height: size,
            background: theme_1.colors.neutral[200],
        } })) : ((0, jsx_runtime_1.jsx)("div", { style: {
            width: size,
            height: size,
            borderRadius: '50%',
            background: theme_1.colors.primary[300],
            color: '#fff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 700,
            fontSize: size / 2,
        }, "aria-label": name || 'Avatar', children: initials }));
};
exports.Avatar = Avatar;
