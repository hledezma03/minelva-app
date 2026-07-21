/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'minelva-blue': '#0077B6',
        'minelva-lightblue': '#00B4D8',
        'minelva-teal': '#2A9D8F',
        'minelva-dark': '#1A2A3A',
        'minelva-gray': '#F5F7FA',
      },
    },
  },
  plugins: [],
}