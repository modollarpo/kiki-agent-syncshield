"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.Form = void 0;
const jsx_runtime_1 = require("react/jsx-runtime");
const react_1 = __importDefault(require("react"));
const Input_1 = require("./Input");
const Button_1 = require("./Button");
const theme_1 = require("../theme");
const Form = ({ fields, onSubmit, submitLabel = 'Submit', initialValues = {}, loading = false, error, className = '', }) => {
    const [values, setValues] = react_1.default.useState(initialValues);
    const handleChange = (e) => {
        const { name, value } = e.target;
        setValues(prev => ({ ...prev, [name]: value }));
    };
    const handleSubmit = (e) => {
        e.preventDefault();
        onSubmit(values);
    };
    return ((0, jsx_runtime_1.jsxs)("form", { className: className, onSubmit: handleSubmit, autoComplete: "off", style: { marginBottom: theme_1.spacing.lg }, children: [fields.map(field => ((0, jsx_runtime_1.jsx)(Input_1.Input, { label: field.label, name: field.name, type: field.type, required: field.required, placeholder: field.placeholder, value: values[field.name] || '', onChange: handleChange }, field.name))), error && (0, jsx_runtime_1.jsx)("div", { style: { color: 'red', fontSize: 13 }, children: error }), (0, jsx_runtime_1.jsx)(Button_1.Button, { type: "submit", disabled: loading, style: { width: '100%' }, children: loading ? 'Loading...' : submitLabel })] }));
};
exports.Form = Form;
