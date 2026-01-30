import React from 'react';
import Sidebar from './Sidebar';
import { Notification } from '@kiki/ui';

interface AppShellProps {
  title?: string;
  children: React.ReactNode;
}

const AppShell: React.FC<AppShellProps> = ({ title, children }) => {
  React.useEffect(() => {
    if (title) {
      document.title = `${title} | KIKI Agent™`;
    }
  }, [title]);

  return (
    <div className="flex min-h-screen bg-gray-950 text-gray-100">
      <Sidebar />
      <main className="flex-1 p-6 overflow-y-auto">
        {/* Notification area (global) */}
        <Notification />
        {children}
      </main>
    </div>
  );
};

export default AppShell;
