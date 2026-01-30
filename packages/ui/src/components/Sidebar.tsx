import React from 'react';
import { colors, radii, spacing, typography } from '../theme';

export interface SidebarItem {
  label: string;
  icon?: React.ReactNode;
  active?: boolean;
  onClick?: () => void;
}

export interface SidebarProps {
  items: SidebarItem[];
  logo?: React.ReactNode;
  footer?: React.ReactNode;
  style?: React.CSSProperties;
}

export const Sidebar: React.FC<SidebarProps> = ({ items, logo, footer, style }) => (
  <aside
    style={{
      width: 260,
      background: 'var(--sidebar-bg, ' + colors.neutral[600] + ')',
      color: colors.neutral[100],
      display: 'flex',
      flexDirection: 'column',
      minHeight: '100vh',
      borderRight: `1px solid ${colors.neutral[400]}`,
      ...style,
    }}
  >
    <div style={{ padding: spacing.lg, fontWeight: typography.headings.fontWeight, fontSize: 22 }}>
      {logo || 'KIKI Agent™'}
    </div>
    <nav style={{ flex: 1 }}>
      {items.map((item, i) => (
        <div
          key={item.label}
          onClick={item.onClick}
          style={{
            display: 'flex',
            alignItems: 'center',
            padding: `${spacing.md}px ${spacing.lg}px`,
            background: item.active ? colors.primary[500] : 'transparent',
            color: item.active ? '#fff' : colors.neutral[100],
            borderRadius: radii.md,
            margin: '4px 8px',
            cursor: 'pointer',
            fontWeight: item.active ? 700 : 500,
            fontSize: 16,
            transition: 'background 0.2s',
          }}
        >
          {item.icon && <span style={{ marginRight: 12 }}>{item.icon}</span>}
          {item.label}
        </div>
      ))}
    </nav>
    {footer && <div style={{ padding: spacing.lg, fontSize: 13, color: colors.neutral[400] }}>{footer}</div>}
  </aside>
);
