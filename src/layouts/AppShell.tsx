import React from 'react';
import Link from 'next/link';
import { Sidebar, SidebarItem } from '@kiki/ui';

const navItems: SidebarItem[] = [
  { label: 'Dashboard', icon: '📊', active: false, onClick: () => {} },
  { label: 'Revenue', icon: '💰', onClick: () => {} },
  { label: 'Agents', icon: '🤖', onClick: () => {} },
  { label: 'Acquisition', icon: '🎯', onClick: () => {} },
  { label: 'Retention', icon: '🔁', onClick: () => {} },
  { label: 'Budget', icon: '💸', onClick: () => {} },
  { label: 'Compliance', icon: '⚖️', onClick: () => {} },
  { label: 'System', icon: '🛠️', onClick: () => {} },
];

export const AppShell: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div style={{ display: 'flex', minHeight: '100vh', background: 'var(--app-bg, #f8f9fa)' }}>
    <Sidebar
      items={navItems.map(item => ({
        ...item,
        onClick: () => {
          // Use Next.js router for navigation
          window.location.href = `/${item.label.toLowerCase()}`;
        },
      }))}
      logo={<Link href="/">KIKI Agent™</Link>}
      footer={<span>© 2026 KIKI Agent™</span>}
    />
    <main style={{ flex: 1, padding: 32 }}>{children}</main>
  </div>
);
