import React from 'react';
import { radii, shadows } from '../theme';

export interface ModalProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
}

export const Modal: React.FC<ModalProps> = ({ open, onClose, title, children }) => {
  if (!open) return null;
  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100vw',
        height: '100vh',
        background: 'rgba(0,0,0,0.4)',
        zIndex: 1000,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
      aria-modal="true"
      role="dialog"
      tabIndex={-1}
      onClick={onClose}
    >
      <div
        style={{
          background: 'var(--modal-bg, #fff)',
          borderRadius: radii.lg,
          boxShadow: shadows.lg,
          minWidth: 400,
          maxWidth: '90vw',
          padding: 32,
          position: 'relative',
        }}
        onClick={e => e.stopPropagation()}
      >
        {title && <h2 style={{ marginTop: 0 }}>{title}</h2>}
        {children}
        <button
          aria-label="Close"
          onClick={onClose}
          style={{
            position: 'absolute',
            top: 16,
            right: 16,
            background: 'none',
            border: 'none',
            fontSize: 24,
            cursor: 'pointer',
          }}
        >
          ×
        </button>
      </div>
    </div>
  );
};
