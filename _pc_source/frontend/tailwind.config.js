/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        ink: '#070A12',
        surface: '#0d0f14',
        raised: '#141821',
        line: '#242a36',
        fg: '#F2E9D8',
        terracotta: '#E07A5F',
        lampAmber: '#F2B45C',
        moonlight: '#7FB2D9',
        thoughtRed: '#D7263D',
        obsidian: '#08080a',
        threadsBg: '#101010',
        threadsCard: '#181818',
      },
      fontFamily: {
        sans: ["'Geist Variable'", "'Geist'", '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        ui: ["'Geist Variable'", "'Geist'", '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        display: ["'Unbounded Variable'", "'Unbounded'", 'sans-serif'],
        grotesque: ["'Bricolage Grotesque Variable'", "'Bricolage Grotesque'", 'sans-serif'],
        mono: ["'Martian Mono'", 'ui-monospace', 'monospace'],
        'mono-tech': ["'Martian Mono'", 'ui-monospace', 'monospace'],
      },
    },
  },
  plugins: [],
};
