import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 7700,
    proxy: {
      // 프론트에서 /api로 시작하는 요청을 보내면 아래 서버 주소로 전달합니다.
      '/api': {
        target: 'http://localhost:8000', // 실제 서버 주소
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})