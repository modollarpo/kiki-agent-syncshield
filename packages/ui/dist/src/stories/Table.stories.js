"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Empty = exports.Default = void 0;
const jsx_runtime_1 = require("react/jsx-runtime");
const Table_1 = require("../Table");
const columns = [
    { key: 'id', label: 'ID' },
    { key: 'name', label: 'Name' },
    { key: 'email', label: 'Email' },
    { key: 'status', label: 'Status', render: (value) => ((0, jsx_runtime_1.jsx)("span", { className: value === 'Active' ? 'text-emerald-400 font-bold' :
                value === 'Pending' ? 'text-yellow-400' :
                    'text-red-400', children: value })) },
];
const data = [
    { id: 1, name: 'Alice', email: 'alice@kiki.com', status: 'Active' },
    { id: 2, name: 'Bob', email: 'bob@kiki.com', status: 'Pending' },
    { id: 3, name: 'Charlie', email: 'charlie@kiki.com', status: 'Suspended' },
];
const meta = {
    title: 'Enterprise/Table',
    component: Table_1.Table,
    tags: ['autodocs'],
    parameters: {
        layout: 'centered',
    },
};
exports.default = meta;
exports.Default = {
    render: () => (0, jsx_runtime_1.jsx)(Table_1.Table, { columns: columns, data: data }),
};
exports.Empty = {
    render: () => (0, jsx_runtime_1.jsx)(Table_1.Table, { columns: columns, data: [] }),
};
