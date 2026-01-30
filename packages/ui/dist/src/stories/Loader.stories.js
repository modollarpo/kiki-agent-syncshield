"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.SmallSlate = exports.LargeEmerald = exports.Default = void 0;
const Loader_1 = require("../Loader");
const meta = {
    title: 'Enterprise/Loader',
    component: Loader_1.Loader,
    tags: ['autodocs'],
    parameters: {
        layout: 'centered',
    },
};
exports.default = meta;
exports.Default = {
    args: {},
};
exports.LargeEmerald = {
    args: {
        size: 64,
        color: '#10b981',
    },
};
exports.SmallSlate = {
    args: {
        size: 16,
        color: '#64748b',
    },
};
