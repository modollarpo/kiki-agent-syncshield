import type { Meta, StoryObj } from '@storybook/react';
import React from 'react';
import { Table, TableColumn } from '../Table';

interface User {
  id: number;
  name: string;
  email: string;
  status: 'Active' | 'Pending' | 'Suspended';
}

const columns: TableColumn<User>[] = [
  { key: 'id', label: 'ID' },
  { key: 'name', label: 'Name' },
  { key: 'email', label: 'Email' },
  { key: 'status', label: 'Status', render: (value) => (
    <span className={
      value === 'Active' ? 'text-emerald-400 font-bold' :
      value === 'Pending' ? 'text-yellow-400' :
      'text-red-400'
    }>{value}</span>
  ) },
];

const data: User[] = [
  { id: 1, name: 'Alice', email: 'alice@kiki.com', status: 'Active' },
  { id: 2, name: 'Bob', email: 'bob@kiki.com', status: 'Pending' },
  { id: 3, name: 'Charlie', email: 'charlie@kiki.com', status: 'Suspended' },
];

const meta: Meta<typeof Table> = {
  title: 'Enterprise/Table',
  component: Table,
  tags: ['autodocs'],
  parameters: {
    layout: 'centered',
  },
};
export default meta;
type Story = StoryObj<typeof Table>;

export const Default: Story = {
  render: () => <Table columns={columns} data={data} />,
};

export const Empty: Story = {
  render: () => <Table columns={columns} data={[]} />,
};
