import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@app': path.resolve(__dirname, './src/app'),
      '@components': path.resolve(__dirname, './src/components'),
      '@screens': path.resolve(__dirname, './src/screens'),
      '@charts': path.resolve(__dirname, './src/charts'),
      '@api': path.resolve(__dirname, './src/api'),
      '@hooks': path.resolve(__dirname, './src/hooks'),
      '@store': path.resolve(__dirname, './src/store'),
      '@theme': path.resolve(__dirname, './src/theme')
    }
  },
  server: {
    port: 5173
  }
});
