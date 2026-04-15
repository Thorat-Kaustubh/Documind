import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./features/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "hsl(222, 47%, 4%)", // Dark Navy
        foreground: "hsl(213, 31%, 91%)",
        card: {
          DEFAULT: "hsl(222, 47%, 7%)",
          foreground: "hsl(213, 31%, 91%)",
        },
        primary: {
          DEFAULT: "hsl(226, 70%, 55%)", // Indigo/Blue
          foreground: "hsl(0, 0%, 100%)",
        },
        accent: {
          DEFAULT: "hsl(226, 70%, 20%)",
          foreground: "hsl(226, 70%, 80%)",
        },
        muted: {
          DEFAULT: "hsl(222, 47%, 15%)",
          foreground: "hsl(215, 20%, 65%)",
        },
        border: "hsl(222, 47%, 12%)",
      },
      borderRadius: {
        xl: "1rem",
        "2xl": "1.5rem",
      },
      boxShadow: {
        premium: "0 8px 32px 0 rgba(0, 0, 0, 0.4)",
        glow: "0 0 15px -3px rgba(59, 130, 246, 0.5)",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};
export default config;
