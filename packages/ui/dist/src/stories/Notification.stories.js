"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Closable = exports.Warning = exports.Error = exports.Success = exports.Info = void 0;
const jsx_runtime_1 = require("react/jsx-runtime");
const react_1 = require("react");
const Notification_1 = require("../Notification");
const meta = {
    title: 'Enterprise/Notification',
    component: Notification_1.Notification,
    tags: ['autodocs'],
    parameters: {
        layout: 'centered',
    },
};
exports.default = meta;
exports.Info = {
    args: {
        type: 'info',
        title: 'Info',
        message: 'This is an informational notification.',
    },
};
exports.Success = {
    args: {
        type: 'success',
        title: 'Success',
        message: 'Your operation completed successfully!',
    },
};
exports.Error = {
    args: {
        type: 'error',
        title: 'Error',
        message: 'Something went wrong. Please try again.',
    },
};
exports.Warning = {
    args: {
        type: 'warning',
        title: 'Warning',
        message: 'This action may have consequences.',
    },
};
exports.Closable = {
    render: (args) => {
        const [open, setOpen] = (0, react_1.useState)(true);
        return open ? ((0, jsx_runtime_1.jsx)(Notification_1.Notification, { ...args, onClose: () => setOpen(false) })) : ((0, jsx_runtime_1.jsx)("button", { className: "px-4 py-2 bg-emerald-600 text-white rounded-lg font-semibold", onClick: () => setOpen(true), children: "Show Notification" }));
    },
    args: {
        type: 'success',
        title: 'Closable',
        message: 'You can close this notification.',
    },
};
