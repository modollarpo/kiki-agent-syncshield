"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Avatar = void 0;
const jsx_runtime_1 = require("react/jsx-runtime");
/**
 * Enterprise Avatar — High-Trust, Dark-Mode, Emerald Accents
 */
const Avatar = ({ src, alt, name, size = 40, className = "" }) => {
    const initials = name
        ? name.split(' ').map((n) => n[0]).join('').toUpperCase().slice(0, 2)
        : '';
    return ((0, jsx_runtime_1.jsx)("div", { className: `inline-flex items-center justify-center rounded-full bg-slate-800 border-2 border-emerald-500/60 shadow-md font-bold text-emerald-300 select-none ${className}`, style: { width: size, height: size, fontSize: size * 0.45 }, "aria-label": alt || name || 'Avatar', children: src ? ((0, jsx_runtime_1.jsx)("img", { src: src, alt: alt || name || 'Avatar', className: "w-full h-full object-cover rounded-full", style: { width: size, height: size } })) : (initials || (0, jsx_runtime_1.jsx)("span", { className: "text-slate-500", children: "?" })) }));
};
exports.Avatar = Avatar;
exports.default = exports.Avatar;
