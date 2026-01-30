"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.ImpactAuditForm = void 0;
const jsx_runtime_1 = require("react/jsx-runtime");
const react_1 = require("react");
const ImpactAuditForm = () => {
    const [monthlyCustomers, setMonthlyCustomers] = (0, react_1.useState)(1000);
    const [ltv, setLtv] = (0, react_1.useState)(120.0);
    const [churn, setChurn] = (0, react_1.useState)(8.0);
    const [result, setResult] = (0, react_1.useState)(null);
    const [loading, setLoading] = (0, react_1.useState)(false);
    const [error, setError] = (0, react_1.useState)(null);
    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setResult(null);
        try {
            const res = await fetch("/api/impact_audit", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    monthly_customers: monthlyCustomers,
                    ltv,
                    churn,
                }),
            });
            if (!res.ok)
                throw new Error("API error");
            const data = await res.json();
            setResult(data);
        }
        catch (err) {
            setError(err.message || "Unknown error");
        }
        finally {
            setLoading(false);
        }
    };
    return ((0, jsx_runtime_1.jsxs)("form", { onSubmit: handleSubmit, className: "p-8 bg-slate-900 border-2 border-emerald-500 rounded-2xl shadow-2xl space-y-6", children: [(0, jsx_runtime_1.jsx)("h3", { className: "text-xl font-bold text-white mb-6", children: "Impact Audit" }), (0, jsx_runtime_1.jsxs)("div", { className: "grid grid-cols-3 gap-6", children: [(0, jsx_runtime_1.jsxs)("div", { children: [(0, jsx_runtime_1.jsx)("label", { className: "block text-slate-300 mb-2", children: "Monthly Customers" }), (0, jsx_runtime_1.jsx)("input", { type: "number", value: monthlyCustomers, onChange: (e) => setMonthlyCustomers(Number(e.target.value)), className: "w-full p-2 rounded bg-slate-800 text-white", min: 1 })] }), (0, jsx_runtime_1.jsxs)("div", { children: [(0, jsx_runtime_1.jsx)("label", { className: "block text-slate-300 mb-2", children: "Avg. LTV ($)" }), (0, jsx_runtime_1.jsx)("input", { type: "number", value: ltv, onChange: (e) => setLtv(Number(e.target.value)), className: "w-full p-2 rounded bg-slate-800 text-white", min: 1, step: 0.01 })] }), (0, jsx_runtime_1.jsxs)("div", { children: [(0, jsx_runtime_1.jsx)("label", { className: "block text-slate-300 mb-2", children: "Churn Rate (%)" }), (0, jsx_runtime_1.jsx)("input", { type: "number", value: churn, onChange: (e) => setChurn(Number(e.target.value)), className: "w-full p-2 rounded bg-slate-800 text-white", min: 0, max: 100, step: 0.01 })] })] }), (0, jsx_runtime_1.jsx)("button", { type: "submit", className: "w-full py-3 bg-emerald-500 hover:bg-emerald-600 text-white font-bold rounded-lg transition-all", disabled: loading, children: loading ? "Calculating..." : "Run Audit" }), error && (0, jsx_runtime_1.jsx)("p", { className: "text-red-500 text-center", children: error }), result && ((0, jsx_runtime_1.jsxs)("div", { className: "mt-8 bg-slate-800 p-6 rounded-lg", children: [(0, jsx_runtime_1.jsx)("h4", { className: "text-lg font-bold text-emerald-400 mb-2", children: "Audit Results" }), (0, jsx_runtime_1.jsxs)("ul", { className: "text-slate-300 space-y-1", children: [(0, jsx_runtime_1.jsxs)("li", { children: ["Projected Uplift: ", (0, jsx_runtime_1.jsx)("b", { children: result.projected_uplift.toLocaleString() })] }), (0, jsx_runtime_1.jsxs)("li", { children: ["KIKI Performance Fee: ", (0, jsx_runtime_1.jsx)("b", { children: result.kiki_performance_fee.toLocaleString() })] }), (0, jsx_runtime_1.jsxs)("li", { children: ["Client Net Profit: ", (0, jsx_runtime_1.jsx)("b", { children: result.client_net_profit.toLocaleString() })] }), (0, jsx_runtime_1.jsxs)("li", { children: ["Conservative Uplift: ", (0, jsx_runtime_1.jsx)("b", { children: result.conservative_uplift.toLocaleString() })] }), (0, jsx_runtime_1.jsxs)("li", { children: ["Aggressive Uplift: ", (0, jsx_runtime_1.jsx)("b", { children: result.aggressive_uplift.toLocaleString() })] }), (0, jsx_runtime_1.jsxs)("li", { children: ["Prospect ID: ", (0, jsx_runtime_1.jsx)("b", { children: result.prospect_id })] })] })] }))] }));
};
exports.ImpactAuditForm = ImpactAuditForm;
exports.default = exports.ImpactAuditForm;
