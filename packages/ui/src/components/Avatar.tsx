import React from 'react';
import { colors, radii } from '../theme';

export interface AvatarProps {
  src?: string;
  name?: string;
  size?: number;
}

export const Avatar: React.FC<AvatarProps> = ({ src, name, size = 40 }) => {
  const initials = name ? name.split(' ').map(n => n[0]).join('').toUpperCase() : '';
  return src ? (
    <img
      src={src}
      alt={name || 'Avatar'}
      width={size}
      height={size}
      style={{
        borderRadius: '50%',
        objectFit: 'cover',
        width: size,
        height: size,
        background: colors.neutral[200],
      }}
    />
  ) : (
    <div
      style={{
        width: size,
        height: size,
        borderRadius: '50%',
        background: colors.primary[300],
        color: '#fff',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontWeight: 700,
        fontSize: size / 2,
      }}
      aria-label={name || 'Avatar'}
    >
      {initials}
    </div>
  );
};
