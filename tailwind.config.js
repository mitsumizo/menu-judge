/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/templates/**/*.html',
    './app/static/js/**/*.js'
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      colors: {
        primary: {
          DEFAULT: '#6366F1', // Indigo 500
          light: '#818CF8',
          dark: '#4F46E5',
        },
        secondary: '#EC4899', // Pink 500
        accent: '#8B5CF6',    // Violet 500
        background: '#FFFFFF', // White
        surface: '#F8FAFC',    // Slate 50
        text: {
          primary: '#0F172A',   // Slate 900
          secondary: '#475569', // Slate 600
        },
      },
      animation: {
        'indeterminate': 'indeterminate 1.5s ease-in-out infinite',
      },
      keyframes: {
        'indeterminate': {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(300%)' },
        },
      },
    },
  },
  plugins: [],
}
