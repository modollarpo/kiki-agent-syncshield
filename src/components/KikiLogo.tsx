import React from 'react';
import { motion } from 'framer-motion';

const KikiLogo = () => (
  <motion.svg
    width="120" height="40" viewBox="0 0 120 40" fill="none"
    xmlns="http://www.w3.org/2000/svg"
    initial={{ opacity: 0, y: -20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.6 }}
  >
    <g fontFamily="'Montserrat', sans-serif" fontWeight="bold">
      <text x="0" y="32" fontSize="32" fill="#fff">
        K
        <tspan x="32" y="32">IKI</tspan>
      </text>
      {/* Stencil gap for 'K' vertical stem */}
      <rect x="8" y="10" width="2" height="22" fill="#22d3ee" />
      <rect x="18" y="10" width="2" height="22" fill="#22d3ee" />
      <text x="70" y="32" fontSize="18" fill="#fff">Agent™</text>
    </g>
  </motion.svg>
);

export default KikiLogo;
