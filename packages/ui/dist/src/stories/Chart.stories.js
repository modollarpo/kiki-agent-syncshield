"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Empty = exports.Default = void 0;
const Chart_1 = require("../Chart");
const meta = {
    title: 'Enterprise/Chart',
    component: Chart_1.Chart,
    tags: ['autodocs'],
    parameters: {
        layout: 'centered',
    },
};
exports.default = meta;
const sampleData = [
    { label: 'SyncBrain', value: 92 },
    { label: 'SyncValue', value: 78 },
    { label: 'SyncFlow', value: 65 },
    { label: 'SyncCreate', value: 88 },
    { label: 'SyncEngage', value: 54 },
    { label: 'SyncShield', value: 99 },
];
exports.Default = {
    args: {
        title: 'Council of Nine — Agent Scores',
        data: sampleData,
    },
};
exports.Empty = {
    args: {
        title: 'No Data',
        data: [],
    },
};
