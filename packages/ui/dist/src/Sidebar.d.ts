import React from "react";
export interface SidebarItem {
    label: string;
    icon?: React.ReactNode;
    active?: boolean;
    onClick?: () => void;
}
export interface SidebarProps {
    items: SidebarItem[];
    className?: string;
}
/**
 * Enterprise Sidebar — High-Trust, Dark-Mode, Emerald Accents
 */
export declare const Sidebar: React.FC<SidebarProps>;
export default Sidebar;
//# sourceMappingURL=Sidebar.d.ts.map