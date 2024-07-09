/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ["./templates/index.html", "./static/script.js"],
    theme: {
        extend: {
            fontFamily: {
                sans: ['"Noto Sans"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
            },
        },
    },
    plugins: [],
}

