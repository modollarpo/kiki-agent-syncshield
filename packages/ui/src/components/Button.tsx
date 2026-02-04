import React from 'react';
import { colors, radii, spacing, typography } from '../theme';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
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
  loading = false,
  disabled,
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
  const isDisabled = Boolean(disabled || loading);
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
        cursor: isDisabled ? 'not-allowed' : 'pointer',
        opacity: isDisabled ? 0.7 : 1,
        transition: 'background 0.2s',
        ...style,
      }}
      disabled={isDisabled}
      aria-busy={loading || undefined}
      {...props}
    >
      <span style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
        {loading && (
          <svg
            aria-hidden
            width={14}
            height={14}
            viewBox="0 0 50 50"
            style={{ display: 'block' }}
          >
            <circle
              cx="25"
              cy="25"
              r="20"
              fill="none"
              stroke="rgba(255,255,255,0.75)"
              strokeWidth="6"
              strokeDasharray="80 40"
              strokeLinecap="round"
            >
              <animateTransform
                attributeName="transform"
                type="rotate"
                from="0 25 25"
                to="360 25 25"
                dur="0.8s"
                repeatCount="indefinite"
              />
            </circle>
          </svg>
        )}
        <span>{children}</span>
      </span>
    </button>
  );
};
