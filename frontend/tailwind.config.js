/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#020617',
        card: '#0f172a',
        primary: '#3b82f6',
        accent: '#10b981',
      }
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
