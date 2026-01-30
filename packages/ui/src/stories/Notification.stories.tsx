import type { Meta, StoryObj } from '@storybook/react';
import React, { useState } from 'react';
import { Notification } from '../Notification';

const meta: Meta<typeof Notification> = {
  title: 'Enterprise/Notification',
  component: Notification,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
  },
};
export default meta;
type Story = StoryObj<typeof Notification>;

export const Info: Story = {
  args: {
    type: 'info',
    title: 'Info',
    message: 'This is an informational notification.',
  },
};

export const Success: Story = {
  args: {
    type: 'success',
    title: 'Success',
    message: 'Your operation completed successfully!',
  },
};

export const Error: Story = {
  args: {
    type: 'error',
    title: 'Error',
    message: 'Something went wrong. Please try again.',
  },
};

export const Warning: Story = {
  args: {
    type: 'warning',
    title: 'Warning',
    message: 'This action may have consequences.',
  },
};

export const Closable: Story = {
  render: (args: any) => {
    const [open, setOpen] = useState(true);
    return open ? (
      <Notification {...args} onClose={() => setOpen(false)} />
    ) : (
      <button
        className="px-4 py-2 bg-emerald-600 text-white rounded-lg font-semibold"
        onClick={() => setOpen(true)}
      >
        Show Notification
      </button>
    );
  },
  args: {
    type: 'success',
    title: 'Closable',
    message: 'You can close this notification.',
  },
};
