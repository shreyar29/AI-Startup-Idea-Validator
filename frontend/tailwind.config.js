/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#0B0F19',
        surface: '#1A2235',
        primary: '#3B82F6',
        primaryDark: '#2563EB',
        secondary: '#10B981',
        textMain: '#F3F4F6',
        textMuted: '#9CA3AF',
        accent: '#8B5CF6'
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
