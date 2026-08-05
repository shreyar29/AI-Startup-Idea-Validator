/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0B1020',
        card: '#161B2D',
        cardHover: '#1C2340',
        primary: '#4F8CFF',
        primaryDark: '#3A6FD8',
        success: '#22C55E',
        warning: '#F59E0B',
        error: '#EF4444',
        surface: '#161B2D',
        border: '#1E2A45',
        textMain: '#E8ECF4',
        textMuted: '#7A8BAD',
        textDim: '#4A5578',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        card: '0 4px 24px 0 rgba(0, 0, 0, 0.25)',
        glow: '0 0 20px rgba(79, 140, 255, 0.15)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
}
