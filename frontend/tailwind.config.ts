import type { Config } from "tailwindcss";

export default {
  content: ["./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        dse: {
          blue: "#003366",
          gold: "#CC9933",
          green: "#228B22",
          red: "#CC3333",
        },
      },
    },
  },
  plugins: [],
} satisfies Config;
