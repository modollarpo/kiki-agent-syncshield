"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Button = void 0;
const jsx_runtime_1 = require("react/jsx-runtime");
require("./button.css");
/** Primary UI component for user interaction */
const Button = ({ primary = false, size = 'medium', backgroundColor, label, ...props }) => {
    const mode = primary ? 'storybook-button--primary' : 'storybook-button--secondary';
    return ((0, jsx_runtime_1.jsx)("button", { type: "button", className: ['storybook-button', `storybook-button--${size}`, mode].join(' '), style: { backgroundColor }, ...props, children: label }));
};
exports.Button = Button;
