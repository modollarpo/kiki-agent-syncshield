import React from 'react';
import { colors, radii, spacing, typography } from '../theme';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
}

const sizeMap = {
  sm: { padding: `${spacing.sm}px ${spacing.md}px`, fontSize: 14 },
  md: { padding: `${spacing.md}px ${spacing.lg}px`, fontSize: 16 },
  lg: { padding: `${spacing.lg}px ${spacing.xl}px`, fontSize: 18 },
};

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  style,
  ...props
}) => {
  let bg, color, border;
  switch (variant) {
    case 'primary':
      bg = colors.primary[500];
      color = '#fff';
      border = 'none';
      break;
    case 'secondary':
      bg = colors.secondary[500];
      color = '#fff';
      border = 'none';
      break;
    case 'danger':
      bg = colors.error;
      color = '#fff';
      border = 'none';
      break;
    case 'ghost':
      bg = 'transparent';
      color = colors.primary[500];
      border = `1px solid ${colors.primary[500]}`;
      break;
    default:
      bg = colors.primary[500];
      color = '#fff';
      border = 'none';
  }
  const { padding, fontSize } = sizeMap[size];
  return (
    <button
      style={{
        background: bg,
        color,
        border,
        borderRadius: radii.md,
        fontFamily: typography.fontFamily,
        fontWeight: typography.headings.fontWeight,
        fontSize,
        padding,
        cursor: 'pointer',
        transition: 'background 0.2s',
        ...style,
      }}
      {...props}
    >
      {children}
    </button>
  );
};
