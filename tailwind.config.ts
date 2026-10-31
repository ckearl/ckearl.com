export default {
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Dark backgrounds
        dark: "#0A0E27",
        midnight: {
          950: "#001233",
          900: "#001a4d",
          800: "#002366",
        },
        // Navy blues
        navy: {
          950: "#011935",
          900: "#012550",
          800: "#013870",
          700: "#014d99",
        },
        // Slate grays
        slate: {
          800: "#2F4F4F",
          700: "#475569",
          600: "#64748b",
          500: "#71859E",
          400: "#8A9CB2",
          300: "#B0BCC8",
          200: "#D4D4D6",
          100: "#EBECEA",
          50: "#F8F8FF",
        },
        // Whites
        platinum: "#E5E4E2",
        offwhite: "#FAFAFA",
        // Blue accents (replacing neon colors)
        electric: {
          DEFAULT: "#4169E1", // Royal blue
          light: "#6495ED",   // Cornflower blue
          dark: "#27509E",
        },
        azure: {
          DEFAULT: "#007FFF",
          light: "#4DA6FF",
          dark: "#0056B3",
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
        mono: ["var(--font-geist-mono)", "monospace"],
      },
    },
  },
};
