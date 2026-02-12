import React from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { Home, BookOpen, Code, Briefcase, PenBox, Info, Phone } from 'lucide-react';
import KikiLogo from './KikiLogo';

const menuItems = [
  { name: 'Home', href: '/', icon: <Home className="w-5 h-5 mr-2" /> },
  { name: 'Docs', href: '/docs', icon: <BookOpen className="w-5 h-5 mr-2" /> },
  { name: 'API', href: '/api', icon: <Code className="w-5 h-5 mr-2" /> },
  { name: 'Case Studies', href: '/case-studies', icon: <Briefcase className="w-5 h-5 mr-2" /> },
  { name: 'Blog', href: '/blog', icon: <PenBox className="w-5 h-5 mr-2" /> },
  { name: 'About', href: '/about', icon: <Info className="w-5 h-5 mr-2" /> },
];


const SovereignHeader = () => (
  <motion.header
    className="w-full border-b border-zinc-800 bg-zinc-950"
    initial={{ opacity: 0, y: -10 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5 }}
  >
    <div className="max-w-7xl mx-auto flex items-center justify-between py-4 px-6">
      <Link href="/">
        <span className="flex items-center gap-2">
          <KikiLogo />
        </span>
      </Link>
      <nav className="flex gap-6">
        {menuItems.map(item => (
          <Link key={item.name} href={item.href} className="flex items-center text-zinc-400 hover:text-cyan-400 font-semibold transition">
            {item.icon}
            {item.name}
          </Link>
        ))}
      </nav>
      <motion.button
        whileHover={{ boxShadow: '0 0 8px 2px #22d3ee', scale: 1.05 }}
        className="bg-white text-black font-bold px-5 py-2 rounded shadow-md transition flex items-center gap-2"
        onClick={() => window.location.href='/contact-sales'}
      >
        <Phone className="w-5 h-5" /> Contact Sales
      </motion.button>
    </div>
  </motion.header>
);

export default SovereignHeader;
