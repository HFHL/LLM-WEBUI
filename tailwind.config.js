/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./templates/**/*.{html,js}"],
  theme: {
    extend: {
      colors: {
        'primary-blue': 'var(--primary-blue)',
        'primary-pink': 'var(--primary-pink)',
      }
    },
  },
  plugins: [],
} 