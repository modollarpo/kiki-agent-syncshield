import type { Meta, StoryObj } from '@storybook/react';
import React, { useState } from 'react';
import { Modal } from '../Modal';

const meta: Meta<typeof Modal> = {
  title: 'Enterprise/Modal',
  component: Modal,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
  },
};
export default meta;
type Story = StoryObj<typeof Modal>;

export const Default: Story = {
  render: (args: any) => {
    const [open, setOpen] = useState(true);
    return (
      <>
        <button
          className="px-4 py-2 bg-emerald-600 text-white rounded-lg font-semibold mb-4"
          onClick={() => setOpen(true)}
        >
          Open Modal
        </button>
        <Modal {...args} open={open} onClose={() => setOpen(false)}>
          <p>This is a high-trust, enterprise modal.<br />
          Use for critical confirmations, onboarding, or secure workflows.</p>
        </Modal>
      </>
    );
  },
  args: {
    title: 'Enterprise Modal',
  },
};
