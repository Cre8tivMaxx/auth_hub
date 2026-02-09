/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        background: "rgb(var(--background))",
        subBackground: "rgb(var(--subBackground))",
        foreground: "rgb(var(--foreground))",
        inputBckground: "rgb(var(--inputBckground))",
        "muted-foreground": "rgb(var(--muted-foreground))",
        buttonBackground :"rgb(var(--buttonBackground))",
        textColor :"rgb(var(--textColor))",
        logoColorText :"rgb(var(--logoColorText))",
        logoColor :"rgb(var(--logoColor))",
        logoBackground :"rgb(var(--logoBackground))",
      },
    },
  },
  plugins: [],
}