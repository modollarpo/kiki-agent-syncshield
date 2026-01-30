import React from 'react';
import { radii, shadows } from '../theme';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  elevation?: 'sm' | 'md' | 'lg';
  children?: React.ReactNode;
  style?: React.CSSProperties;
}

// Add index signature to shadows for TS
const _shadows: Record<string, string> = shadows as Record<string, string>;

export const Card: React.FC<CardProps> = ({ children, elevation = 'md', style, ...props }) => (
  <div
    style={{
      borderRadius: radii.lg,
      boxShadow: _shadows[elevation],
      background: 'var(--card-bg, #fff)',
      padding: 24,
      ...style,
    }}
    {...props}
  >
    {children}
  </div>
);
