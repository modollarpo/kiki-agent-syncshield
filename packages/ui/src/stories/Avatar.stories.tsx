import type { Meta, StoryObj } from '@storybook/react';
import React from 'react';
import { Avatar } from '../Avatar';

const meta: Meta<typeof Avatar> = {
  title: 'Enterprise/Avatar',
  component: Avatar,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
  },
};
export default meta;
type Story = StoryObj<typeof Avatar>;

export const Initials: Story = {
  args: {
    name: 'Alice Kiki',
    size: 48,
  },
};

export const Image: Story = {
  args: {
    src: 'https://randomuser.me/api/portraits/women/44.jpg',
    alt: 'Alice Kiki',
    size: 48,
  },
};

export const Small: Story = {
  args: {
    name: 'Bob',
    size: 24,
  },
};

export const Large: Story = {
  args: {
    name: 'Charlie Delta',
    size: 80,
  },
};

export const NoName: Story = {
  args: {
    size: 40,
  },
};
