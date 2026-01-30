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
export const Sidebar: React.FC<SidebarProps> = ({ items, className = "" }) => (
  <aside className={`w-64 bg-slate-950 border-r border-emerald-500/20 min-h-screen flex flex-col shadow-2xl ${className}`}>
    <div className="p-6 text-2xl font-bold text-emerald-400 tracking-tight font-sans border-b border-emerald-500/10">
      KIKI Agent™
    </div>
    <nav className="flex-1 p-4 space-y-2">
      {items.map((item, i) => (
        <button
          key={item.label}
          className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg font-semibold text-left transition
            ${item.active ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/40' :
              'text-slate-300 hover:bg-slate-800/60'}
          `}
          onClick={item.onClick}
        >
          {item.icon && <span className="text-xl">{item.icon}</span>}
          {item.label}
        </button>
      ))}
    </nav>
    <div className="p-4 text-xs text-slate-500 border-t border-emerald-500/10">© 2026 KIKI Agent™</div>
  </aside>
);

export default Sidebar;
