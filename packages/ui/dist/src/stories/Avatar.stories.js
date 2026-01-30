"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.NoName = exports.Large = exports.Small = exports.Image = exports.Initials = void 0;
const Avatar_1 = require("../Avatar");
const meta = {
    title: 'Enterprise/Avatar',
    component: Avatar_1.Avatar,
    tags: ['autodocs'],
    parameters: {
        layout: 'centered',
    },
};
exports.default = meta;
exports.Initials = {
    args: {
        name: 'Alice Kiki',
        size: 48,
    },
};
exports.Image = {
    args: {
        src: 'https://randomuser.me/api/portraits/women/44.jpg',
        alt: 'Alice Kiki',
        size: 48,
    },
};
exports.Small = {
    args: {
        name: 'Bob',
        size: 24,
    },
};
exports.Large = {
    args: {
        name: 'Charlie Delta',
        size: 80,
    },
};
exports.NoName = {
    args: {
        size: 40,
    },
};
