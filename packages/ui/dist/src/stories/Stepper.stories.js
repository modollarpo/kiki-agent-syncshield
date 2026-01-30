"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.FirstStep = exports.AllComplete = exports.Default = void 0;
const Stepper_1 = require("../Stepper");
const meta = {
    title: 'Enterprise/Stepper',
    component: Stepper_1.Stepper,
    tags: ['autodocs'],
    parameters: {
        layout: 'centered',
    },
};
exports.default = meta;
const steps = [
    { label: 'Connect APIs', description: 'Google, Meta, Stripe', completed: true },
    { label: 'Ingest Data', description: 'Sync historical data', completed: true },
    { label: 'Configure Brand', description: 'Logos, colors, assets', current: true },
    { label: 'Authorize Budget', description: 'Approve daily spend' },
    { label: 'Deploy Agents', description: 'Council of Nine' },
];
exports.Default = {
    args: {
        steps,
    },
};
exports.AllComplete = {
    args: {
        steps: steps.map(s => ({ ...s, completed: true, current: false })),
    },
};
exports.FirstStep = {
    args: {
        steps: steps.map((s, i) => ({ ...s, completed: false, current: i === 0 })),
    },
};
