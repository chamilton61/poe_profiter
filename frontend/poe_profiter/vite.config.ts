import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react({
      babel: {
        plugins: [['babel-plugin-react-compiler']],
      },
    }),
  ],
  server: {
    allowedHosts: ['poeprofiter.com'],
    proxy: {
      '/api/trade2': {
        target: 'https://www.pathofexile.com',
        changeOrigin: true,
        configure: (proxy) => {
          proxy.on('proxyReq', (proxyReq, req) => {
            const sessid = req.headers['x-poesessid'];
            if (sessid) {
              const val = Array.isArray(sessid) ? sessid[0] : sessid;
              proxyReq.setHeader('Cookie', `POESESSID=${val}`);
            }
            proxyReq.removeHeader('x-poesessid');
            proxyReq.setHeader(
              'User-Agent',
              'poe-profiter/1.0 dev@poe-profiter.local',
            );
          });
        },
      },
    },
  },
  base: './'
})
