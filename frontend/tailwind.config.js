/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                background: "#09090b",
                foreground: "#fafafa",
                primary: "#3b82f6",
                secondary: "#a1a1aa",
                accent: "#8b5cf6",
                success: "#22c55e",
                warning: "#eab308",
                error: "#ef4444",
                card: "#18181b",
                border: "#27272a",
            },
            fontFamily: {
                sans: ['Inter', 'sans-serif'],
                mono: ['Fira Code', 'monospace'],
            },
        },
    },
    plugins: [],
}
