import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        intertight: ['Inter Tight', 'sans-serif'],
      },
      colors: {
        zinc: {
          950: '#0a0a0a',
          900: '#18181b',
          800: '#27272a',
        },
        cyan: {
          400: '#22d3ee',
          300: '#67e8f9',
        },
      },
    },
  },
  plugins: [],
};

export default config;
