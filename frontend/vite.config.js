import path from 'path'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import Icons from 'unplugin-icons/vite'

// https://vitejs.dev/config/
export default defineConfig({
  base: '/assets/frappe_vault/frontend/',
  plugins: [
    vue(),
    Icons({
      autoInstall: true,
      compiler: 'vue3',
    }),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  build: {
    outDir: '../frappe_vault/public/frontend',
    emptyOutDir: true,
    target: 'es2015',
    rollupOptions: {
      output: {
        entryFileNames: 'assets/index.js',
        chunkFileNames: 'assets/[name]-[hash].js',
        assetFileNames: (assetInfo) => {
          if (assetInfo.name === 'index.css') {
            return 'assets/index.css'
          }
          return 'assets/[name]-[hash][extname]'
        },
        manualChunks: {
          'frappe-ui': ['frappe-ui'],
        },
      },
    },
  },
  server: {
    port: 8080,
    proxy: {
      '^/(api|app|files|private)': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        ws: true,
      },
    },
  },
  optimizeDeps: {
    include: [
      'frappe-ui > feather-icons',
      'highlight.js',
      'highlight.js/lib/core',
      'interactjs',
      'debug'
    ],
  },
})
