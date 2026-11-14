import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev: Vite on :5173 proxies /api to FastAPI on :8000.
// /landing-pages/* gets CORS so ThreeUI's sandboxed iframe can import its modules.
export default defineConfig({
  plugins: [
    react(),
    {
      name: "landing-page-cors",
      configureServer(server) {
        server.middlewares.use((req, res, next) => {
          if (req.url?.startsWith("/landing-pages/")) res.setHeader("Access-Control-Allow-Origin", "*");
          next();
        });
      },
    },
  ],
  server: { proxy: { "/api": "http://127.0.0.1:8000" } },
  build: { chunkSizeWarningLimit: 900 },
});
