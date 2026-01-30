import React from 'react';
import { colors, radii, shadows, spacing } from '../theme';

export interface NotificationProps {
  message: string;
  type?: 'info' | 'success' | 'warning' | 'error';
  onClose?: () => void;
}

const typeMap = {
  info: colors.info,
  success: colors.success,
  warning: colors.warning,
  error: colors.error,
};

export const Notification: React.FC<NotificationProps> = ({ message, type = 'info', onClose }) => (
  <div
    style={{
      background: typeMap[type],
      color: '#fff',
      borderRadius: radii.md,
      boxShadow: shadows.md,
      padding: `${spacing.md}px ${spacing.lg}px`,
      display: 'flex',
      alignItems: 'center',
      marginBottom: spacing.md,
      position: 'relative',
      minWidth: 320,
      maxWidth: 480,
    }}
    role="alert"
  >
    <span style={{ flex: 1 }}>{message}</span>
    {onClose && (
      <button
        onClick={onClose}
        aria-label="Close notification"
        style={{
          background: 'none',
          border: 'none',
          color: '#fff',
          fontSize: 18,
          marginLeft: spacing.md,
          cursor: 'pointer',
        }}
      >
        ×
      </button>
    )}
  </div>
);
