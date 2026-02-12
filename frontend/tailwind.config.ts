import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        card: "hsl(var(--card))",
        "card-foreground": "hsl(var(--card-foreground))",
        muted: "hsl(var(--muted))",
        "muted-foreground": "hsl(var(--muted-foreground))",
        border: "hsl(var(--border))",
        primary: "hsl(var(--primary))",
        "primary-foreground": "hsl(var(--primary-foreground))",
        accent: "hsl(var(--accent))",
      },
      borderRadius: {
        xl: "1rem",
      },
      backgroundImage: {
        "hero-grid": "radial-gradient(circle at 1px 1px, hsl(var(--border) / 0.35) 1px, transparent 0)",
      },
      boxShadow: {
        soft: "0 24px 60px -24px rgba(2, 26, 48, 0.35)",
      },
    },
  },
  plugins: [],
};

export default config;
