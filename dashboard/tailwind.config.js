/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        guardian: {
          bg: "#0a0e17",
          card: "#111827",
          accent: "#22d3ee",
          danger: "#f43f5e",
          warn: "#fbbf24",
          safe: "#34d399",
        },
      },
    },
  },
  plugins: [],
};
