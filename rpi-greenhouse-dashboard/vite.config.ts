import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
    server: {
        proxy: {
            '/api': {
                target: 'http://localhost:4000', // backend server
                changeOrigin: true, // ensure the request appears to come from the frontend server
                rewrite: (path) => path.replace(/^\/api/, ''), // remove '/api' prefix
            },
        },
    },
})
