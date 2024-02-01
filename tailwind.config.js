/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
      "./src/templates/**/*.html"
    ],
    theme: {
        extend: {},
    },
    plugins: [
        require('@tailwindcss/typography'),
        require("daisyui")
    ],
    daisyui:{
        themes:[
            "emerald",
            "dark",
            "bumblebee",
            "light"
        ],
        styled: true,
        rtl: false,
        base: true,
        utils: true,
        logs: true,
        themeRoot: "root"
    }
}
