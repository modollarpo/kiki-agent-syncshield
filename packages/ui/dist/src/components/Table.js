"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.Table = Table;
const jsx_runtime_1 = require("react/jsx-runtime");
const theme_1 = require("../theme");
function Table({ columns, data, emptyText = 'No data' }) {
    return ((0, jsx_runtime_1.jsx)("div", { style: { overflowX: 'auto' }, children: (0, jsx_runtime_1.jsxs)("table", { style: {
                width: '100%',
                borderCollapse: 'collapse',
                fontFamily: theme_1.typography.fontFamily,
                fontSize: 15,
            }, children: [(0, jsx_runtime_1.jsx)("thead", { children: (0, jsx_runtime_1.jsx)("tr", { children: columns.map(col => ((0, jsx_runtime_1.jsx)("th", { style: {
                                textAlign: col.align || 'left',
                                padding: theme_1.spacing.sm,
                                background: theme_1.colors.neutral[200],
                                color: theme_1.colors.neutral[600],
                                fontWeight: theme_1.typography.headings.fontWeight,
                                borderBottom: `2px solid ${theme_1.colors.neutral[300]}`,
                            }, children: col.label }, String(col.key)))) }) }), (0, jsx_runtime_1.jsx)("tbody", { children: data.length === 0 ? ((0, jsx_runtime_1.jsx)("tr", { children: (0, jsx_runtime_1.jsx)("td", { colSpan: columns.length, style: { textAlign: 'center', padding: theme_1.spacing.lg }, children: emptyText }) })) : (data.map((row, i) => ((0, jsx_runtime_1.jsx)("tr", { style: { background: i % 2 ? theme_1.colors.neutral[100] : '#fff' }, children: columns.map(col => ((0, jsx_runtime_1.jsx)("td", { style: {
                                textAlign: col.align || 'left',
                                padding: theme_1.spacing.sm,
                                borderBottom: `1px solid ${theme_1.colors.neutral[200]}`,
                            }, children: col.render ? col.render(row) : String(row[col.key]) }, String(col.key)))) }, i)))) })] }) }));
}
