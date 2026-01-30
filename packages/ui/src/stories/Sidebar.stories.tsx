import React from "react";
import type { Meta, StoryObj } from "@storybook/react";
import { Sidebar } from "../index";

const meta: Meta<typeof Sidebar> = {
  title: "Components/Sidebar",
  component: Sidebar,
  tags: ["autodocs"],
  parameters: {
    layout: "fullscreen",
    backgrounds: { default: "dark" },
  },
};
export default meta;

type Story = StoryObj<typeof Sidebar>;

export const Default: Story = {
  args: {
    items: [
      { label: "Dashboard", icon: "🏠", active: true },
      { label: "Agents", icon: "🤖" },
      { label: "Billing", icon: "💳" },
      { label: "Settings", icon: "⚙️" },
    ],
    logo: "KIKI Agent™",
    footer: "© 2024 KIKI Agent™",
  },
};

export const WithCustomFooter: Story = {
  args: {
    items: [
      { label: "Dashboard", icon: "🏠" },
      { label: "Agents", icon: "🤖", active: true },
      { label: "Billing", icon: "💳" },
      { label: "Settings", icon: "⚙️" },
    ],
    logo: <span style={{ fontWeight: 700 }}>KIKI Agent™</span>,
    footer: <div style={{ fontSize: 12 }}>Custom Footer Content</div>,
  },
};
