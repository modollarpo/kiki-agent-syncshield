import React from 'react';
export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
    elevation?: 'sm' | 'md' | 'lg';
    children?: React.ReactNode;
    style?: React.CSSProperties;
}
export declare const Card: React.FC<CardProps>;
//# sourceMappingURL=Card.d.ts.map