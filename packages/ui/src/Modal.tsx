import React from "react";

export interface ModalProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
}

/**
 * Enterprise Modal — High-Trust, Dark-Mode, Emerald Accents
 */
export const Modal: React.FC<ModalProps> = ({ open, onClose, title, children }) => {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm">
      <div className="bg-slate-900 rounded-2xl shadow-2xl border border-emerald-500/40 w-full max-w-lg p-8 relative">
        <button
          className="absolute top-4 right-4 text-emerald-400 hover:text-emerald-300 text-2xl font-bold focus:outline-none"
          onClick={onClose}
          aria-label="Close modal"
        >
          ×
        </button>
        {title && <h2 className="text-2xl font-bold text-emerald-400 mb-4 font-sans tracking-tight">{title}</h2>}
        <div className="text-slate-200 font-sans text-base">{children}</div>
      </div>
    </div>
  );
};

export default Modal;
