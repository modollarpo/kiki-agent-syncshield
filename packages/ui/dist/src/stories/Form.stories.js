"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.WithTextarea = exports.Registration = exports.Login = void 0;
const index_1 = require("../index");
const meta = {
    title: "Components/Form",
    component: index_1.Form,
    tags: ["autodocs"],
    parameters: {
        layout: "centered",
        backgrounds: { default: "dark" },
    },
};
exports.default = meta;
exports.Login = {
    args: {
        fields: [
            { name: "email", label: "Email", type: "email", required: true, placeholder: "user@email.com" },
            { name: "password", label: "Password", type: "password", required: true, placeholder: "••••••••" },
        ],
        submitLabel: "Sign In",
        onSubmit: (values) => alert(JSON.stringify(values, null, 2)),
    },
};
exports.Registration = {
    args: {
        fields: [
            { name: "name", label: "Name", type: "text", required: true, placeholder: "Your Name" },
            { name: "email", label: "Email", type: "email", required: true, placeholder: "user@email.com" },
            { name: "role", label: "Role", type: "select", options: [{ label: "Admin", value: "admin" }, { label: "User", value: "user" }], required: true, placeholder: "Select role" },
            { name: "tos", label: "Accept Terms", type: "checkbox", required: true },
        ],
        submitLabel: "Register",
        onSubmit: (values) => alert(JSON.stringify(values, null, 2)),
    },
};
exports.WithTextarea = {
    args: {
        fields: [
            { name: "feedback", label: "Feedback", type: "textarea", required: true, placeholder: "Your feedback..." },
        ],
        submitLabel: "Send Feedback",
        onSubmit: (values) => alert(JSON.stringify(values, null, 2)),
    },
};
