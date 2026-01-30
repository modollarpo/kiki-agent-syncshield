import React from 'react';
import { colors, radii, spacing, typography } from '../theme';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export const Input: React.FC<InputProps> = ({ label, error, style, ...props }) => (
  <div style={{ marginBottom: spacing.md }}>
    {label && (
      <label
        style={{
          display: 'block',
          marginBottom: 4,
          fontWeight: typography.headings.fontWeight,
          color: colors.neutral[600],
        }}
      >
        {label}
      </label>
    )}
    <input
      style={{
        width: '100%',
        padding: `${spacing.sm}px ${spacing.md}px`,
        borderRadius: radii.sm,
        border: `1px solid ${error ? colors.error : colors.neutral[300]}`,
        fontFamily: typography.fontFamily,
        fontSize: 16,
        outline: 'none',
        boxSizing: 'border-box',
      }}
      {...props}
    />
    {error && <div style={{ color: colors.error, fontSize: 12 }}>{error}</div>}
  </div>
);
