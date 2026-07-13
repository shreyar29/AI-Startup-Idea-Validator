/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        outfit: ['Outfit', 'sans-serif'],
      },
      colors: {
        background: '#0B0F19',
        surface: '#131B2D',
        primary: '#06b6d4',
        primaryHover: '#0891b2',
        textMain: '#F3F4F6',
        textMuted: '#9CA3AF',
        accent: '#D946EF',
      }
    },
  },
  plugins: [],
}
