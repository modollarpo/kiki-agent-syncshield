import type { Meta, StoryObj } from '@storybook/react';
import React from 'react';
import { Chart } from '../Chart';

const meta: Meta<typeof Chart> = {
  title: 'Enterprise/Chart',
  component: Chart,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
  },
};
export default meta;
type Story = StoryObj<typeof Chart>;

const sampleData = [
  { label: 'SyncBrain', value: 92 },
  { label: 'SyncValue', value: 78 },
  { label: 'SyncFlow', value: 65 },
  { label: 'SyncCreate', value: 88 },
  { label: 'SyncEngage', value: 54 },
  { label: 'SyncShield', value: 99 },
];

export const Default: Story = {
  args: {
    title: 'Council of Nine — Agent Scores',
    data: sampleData,
  },
};

export const Empty: Story = {
  args: {
    title: 'No Data',
    data: [],
  },
};
