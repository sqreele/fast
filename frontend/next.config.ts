import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  // Remove the non-existent experimental property
  eslint: {
    // Ignore ESLint during builds for production deployment
    ignoreDuringBuilds: true,
  },
};

export default nextConfig;