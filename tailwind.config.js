/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/templates/**/*.html',
    './app/static/js/**/*.js'
  ],
  darkMode: 'class',
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
        background: '#0B0F19', // Darker rich blue-black
        surface: '#111827',    // Gray 900
        text: {
          primary: '#F9FAFB',
          secondary: '#9CA3AF',
        },
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'hero-pattern': "url('/static/images/grid.svg')",
      },
      animation: {
        'shine': 'shine 1.5s infinite',
        'gradient-text': 'gradient-text 8s ease infinite',
      },
      keyframes: {
        shine: {
          '100%': { left: '125%' },
        },
        'gradient-text': {
          '0%, 100%': {
            'background-size': '200% 200%',
            'background-position': 'left center'
          },
          '50%': {
            'background-size': '200% 200%',
            'background-position': 'right center'
          },
        },
      },
    },
  },
  plugins: [],
}
