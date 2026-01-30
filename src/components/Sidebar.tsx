import React from 'react';
import Link from 'next/link';
import { Sidebar as KikiSidebar, Avatar } from '@kiki/ui';

const navLinks = [
  { href: '/dashboard', label: 'Dashboard' },
  { href: '/billing', label: 'Billing' },
  { href: '/profile', label: 'Profile' },
  { href: '/settings', label: 'Settings' },
  { href: '/users', label: 'Users' },
  { href: '/teams', label: 'Teams' },
  { href: '/activity', label: 'Activity' },
  { href: '/audit', label: 'Audit' },
  { href: '/notifications', label: 'Notifications' },
  { href: '/support', label: 'Support' },
  { href: '/legal', label: 'Legal' },
  { href: '/integrations', label: 'Integrations' },
  { href: '/api-keys', label: 'API Keys' },
  { href: '/usage', label: 'Usage' },
  { href: '/reports', label: 'Reports' },
  { href: '/admin', label: 'Admin' },
];

const Sidebar = () => (
  <KikiSidebar>
    <div className="flex flex-col items-center py-6">
      <Avatar size="lg" name="KIKI Agent" />
      <span className="mt-2 font-bold text-lg">KIKI Agent™</span>
    </div>
    <nav className="flex-1">
      <ul className="space-y-2">
        {navLinks.map(link => (
          <li key={link.href}>
            <Link href={link.href} legacyBehavior>
              <a className="block px-4 py-2 rounded hover:bg-gray-800 transition-colors">
                {link.label}
              </a>
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  </KikiSidebar>
);

export default Sidebar;
