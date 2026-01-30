import type { Meta, StoryObj } from '@storybook/react';
import React from 'react';
import { Stepper } from '../Stepper';

const meta: Meta<typeof Stepper> = {
  title: 'Enterprise/Stepper',
  component: Stepper,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
  },
};
export default meta;
type Story = StoryObj<typeof Stepper>;

const steps = [
  { label: 'Connect APIs', description: 'Google, Meta, Stripe', completed: true },
  { label: 'Ingest Data', description: 'Sync historical data', completed: true },
  { label: 'Configure Brand', description: 'Logos, colors, assets', current: true },
  { label: 'Authorize Budget', description: 'Approve daily spend' },
  { label: 'Deploy Agents', description: 'Council of Nine' },
];

export const Default: Story = {
  args: {
    steps,
  },
};

export const AllComplete: Story = {
  args: {
    steps: steps.map(s => ({ ...s, completed: true, current: false })),
  },
};

export const FirstStep: Story = {
  args: {
    steps: steps.map((s, i) => ({ ...s, completed: false, current: i === 0 })),
  },
};
