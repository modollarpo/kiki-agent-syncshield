import React from 'react';
import { colors } from '../theme';

export interface LoaderProps {
  size?: number;
  color?: string;
}

export const Loader: React.FC<LoaderProps> = ({ size = 32, color }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 50 50"
    style={{ display: 'block', margin: 'auto' }}
    aria-label="Loading"
  >
    <circle
      cx="25"
      cy="25"
      r="20"
      fill="none"
      stroke={color || colors.primary[500]}
      strokeWidth="5"
      strokeDasharray="31.4 31.4"
      strokeLinecap="round"
      transform="rotate(-90 25 25)"
    >
      <animateTransform
        attributeName="transform"
        type="rotate"
        from="0 25 25"
        to="360 25 25"
        dur="1s"
        repeatCount="indefinite"
      />
    </circle>
  </svg>
);
