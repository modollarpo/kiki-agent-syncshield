import React from "react";
import type { Meta, StoryObj } from "@storybook/react";
import { Form } from "../index";

const meta: Meta<typeof Form> = {
  title: "Components/Form",
  component: Form,
  tags: ["autodocs"],
  parameters: {
    layout: "centered",
    backgrounds: { default: "dark" },
  },
};
export default meta;

type Story = StoryObj<typeof Form>;

export const Login: Story = {
  args: {
    fields: [
      { name: "email", label: "Email", type: "email", required: true, placeholder: "user@email.com" },
      { name: "password", label: "Password", type: "password", required: true, placeholder: "••••••••" },
    ],
    submitLabel: "Sign In",
    onSubmit: (values: Record<string, any>) => alert(JSON.stringify(values, null, 2)),
  },
};

export const Registration: Story = {
  args: {
    fields: [
      { name: "name", label: "Name", type: "text", required: true, placeholder: "Your Name" },
      { name: "email", label: "Email", type: "email", required: true, placeholder: "user@email.com" },
      { name: "role", label: "Role", type: "select", options: [ { label: "Admin", value: "admin" }, { label: "User", value: "user" } ], required: true, placeholder: "Select role" },
      { name: "tos", label: "Accept Terms", type: "checkbox", required: true },
    ],
    submitLabel: "Register",
    onSubmit: (values: Record<string, any>) => alert(JSON.stringify(values, null, 2)),
  },
};

export const WithTextarea: Story = {
  args: {
    fields: [
      { name: "feedback", label: "Feedback", type: "textarea", required: true, placeholder: "Your feedback..." },
    ],
    submitLabel: "Send Feedback",
    onSubmit: (values: Record<string, any>) => alert(JSON.stringify(values, null, 2)),
  },
};
