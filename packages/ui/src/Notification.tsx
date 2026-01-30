import React from "react";

export interface NotificationProps {
  type?: "success" | "error" | "warning" | "info";
  title?: string;
  message: string;
  onClose?: () => void;
  className?: string;
}

const typeStyles = {
  success: "bg-emerald-900 border-emerald-500 text-emerald-300",
  error: "bg-red-900 border-red-500 text-red-300",
  warning: "bg-yellow-900 border-yellow-500 text-yellow-300",
  info: "bg-slate-800 border-slate-500 text-slate-200",
};

export const Notification: React.FC<NotificationProps> = ({
  type = "info",
  title,
  message,
  onClose,
  className = "",
}) => (
  <div
    className={`relative rounded-xl border shadow-lg px-6 py-4 flex items-start gap-4 ${typeStyles[type]} ${className}`}
    role="alert"
  >
    <div className="flex-1">
      {title && <div className="font-bold text-lg mb-1 font-sans">{title}</div>}
      <div className="text-base font-sans">{message}</div>
    </div>
    {onClose && (
      <button
        className="absolute top-2 right-2 text-xl text-emerald-400 hover:text-emerald-200 focus:outline-none"
        onClick={onClose}
        aria-label="Close notification"
      >
        ×
      </button>
    )}
  </div>
);

export default Notification;
