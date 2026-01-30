import type { Meta, StoryObj } from '@storybook/react';
import React from 'react';
import { Loader } from '../Loader';

const meta: Meta<typeof Loader> = {
  title: 'Enterprise/Loader',
  component: Loader,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
  },
};
export default meta;
type Story = StoryObj<typeof Loader>;

export const Default: Story = {
  args: {},
};

export const LargeEmerald: Story = {
  args: {
    size: 64,
    color: '#10b981',
  },
};

export const SmallSlate: Story = {
  args: {
    size: 16,
    color: '#64748b',
  },
};
