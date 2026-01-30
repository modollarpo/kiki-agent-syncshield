"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const jsx_runtime_1 = require("react/jsx-runtime");
const react_1 = require("react");
const Form = ({ fields, onSubmit, submitLabel = "Submit", initialValues = {}, loading = false, error, className = "", }) => {
    const [values, setValues] = (0, react_1.useState)(initialValues);
    const [touched, setTouched] = (0, react_1.useState)({});
    const handleChange = (e) => {
        const { name, value, type } = e.target;
        let fieldValue = value;
        if (type === "checkbox" && e.target instanceof HTMLInputElement) {
            fieldValue = e.target.checked;
        }
        setValues((prev) => ({
            ...prev,
            [name]: fieldValue,
        }));
        setTouched((prev) => ({ ...prev, [name]: true }));
    };
    const handleSubmit = (e) => {
        e.preventDefault();
        onSubmit(values);
    };
    return ((0, jsx_runtime_1.jsxs)("form", { className: `bg-zinc-900 rounded-lg p-6 shadow-lg space-y-4 ${className}`, onSubmit: handleSubmit, autoComplete: "off", children: [fields.map((field) => ((0, jsx_runtime_1.jsxs)("div", { className: "flex flex-col gap-1", children: [(0, jsx_runtime_1.jsxs)("label", { htmlFor: field.name, className: "text-zinc-200 font-medium", children: [field.label, field.required && (0, jsx_runtime_1.jsx)("span", { className: "text-red-500 ml-1", children: "*" })] }), field.type === "textarea" ? ((0, jsx_runtime_1.jsx)("textarea", { id: field.name, name: field.name, required: field.required, placeholder: field.placeholder, value: values[field.name] || "", onChange: handleChange, className: "bg-zinc-800 text-zinc-100 rounded px-3 py-2 border border-zinc-700 focus:border-blue-500 focus:outline-none" })) : field.type === "select" ? ((0, jsx_runtime_1.jsxs)("select", { id: field.name, name: field.name, required: field.required, value: values[field.name] || "", onChange: handleChange, className: "bg-zinc-800 text-zinc-100 rounded px-3 py-2 border border-zinc-700 focus:border-blue-500 focus:outline-none", children: [(0, jsx_runtime_1.jsx)("option", { value: "", disabled: true, children: field.placeholder || "Select..." }), field.options?.map((opt) => ((0, jsx_runtime_1.jsx)("option", { value: opt.value, children: opt.label }, opt.value)))] })) : ((0, jsx_runtime_1.jsx)("input", { id: field.name, name: field.name, type: field.type, required: field.required, placeholder: field.placeholder, value: field.type === "checkbox" ? undefined : values[field.name] || "", checked: field.type === "checkbox" ? !!values[field.name] : undefined, onChange: handleChange, className: `bg-zinc-800 text-zinc-100 rounded px-3 py-2 border border-zinc-700 focus:border-blue-500 focus:outline-none ${field.type === "checkbox" ? "w-5 h-5 mt-1" : ""}` }))] }, field.name))), error && (0, jsx_runtime_1.jsx)("div", { className: "text-red-500 text-sm", children: error }), (0, jsx_runtime_1.jsx)("button", { type: "submit", className: "w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded disabled:opacity-60", disabled: loading, children: loading ? "Loading..." : submitLabel })] }));
};
exports.default = Form;
