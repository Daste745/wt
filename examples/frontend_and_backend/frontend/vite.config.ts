import { defineConfig, loadEnv } from "vite";

export default defineConfig(({ mode }) => {
  const cwd = process.cwd();
  const env = loadEnv(mode, cwd, "VITE_");

  return {
    server: {
      port: parseInt(env.VITE_PORT || "3000"),
    },
  };
});
