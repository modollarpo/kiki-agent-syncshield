import React from 'react';
export interface SidebarItem {
    label: string;
    icon?: React.ReactNode;
    active?: boolean;
    onClick?: () => void;
}
export interface SidebarProps {
    items: SidebarItem[];
    logo?: React.ReactNode;
    footer?: React.ReactNode;
    style?: React.CSSProperties;
}
export declare const Sidebar: React.FC<SidebarProps>;
//# sourceMappingURL=Sidebar.d.ts.map