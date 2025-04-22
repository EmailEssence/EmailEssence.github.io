import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import { configDefaults } from 'vitest/config'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'build'
  },
  test: {
    coverage:{
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
    },
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/tests/setup.js',
    include: ['src/tests/**/*.test.jsx'],
    exclude: [...configDefaults.exclude, 'node_modules'],
  },
})
