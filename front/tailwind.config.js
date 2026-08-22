/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        airlock: {
          bg: '#0f1117',
          card: '#161b22',
          border: '#30363d',
          input: '#0d1117',
          text: '#e1e4e8',
          muted: '#8b949e',
          subtle: '#484f58',
          green: '#3fb950',
          'green-hover': '#2ea043',
          red: '#f85149',
          yellow: '#d29922',
          blue: '#58a6ff',
          cyan: '#39d2c0',
        },
      },
      fontFamily: {
        mono: ['"Fira Code"', '"JetBrains Mono"', 'monospace'],
      },
    },
  },
  plugins: [],
}
