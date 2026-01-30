import React from "react";

export interface LoaderProps {
  size?: number;
  color?: string;
  className?: string;
}

/**
 * Enterprise Loader — High-Trust, Dark-Mode, Emerald Accents
 */
export const Loader: React.FC<LoaderProps> = ({ size = 32, color = "#10b981", className = "" }) => (
  <svg
    className={`animate-spin ${className}`}
    width={size}
    height={size}
    viewBox="0 0 50 50"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    role="status"
    aria-label="Loading"
  >
    <circle
      cx="25"
      cy="25"
      r="20"
      stroke="#334155"
      strokeWidth="6"
      fill="none"
    />
    <path
      d="M45 25a20 20 0 1 1-40 0"
      stroke={color}
      strokeWidth="6"
      strokeLinecap="round"
      fill="none"
    />
  </svg>
);

export default Loader;
