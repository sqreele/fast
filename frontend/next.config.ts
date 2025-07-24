import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Remove the non-existent experimental property
  eslint: {
    // Optional: Ignore ESLint during builds if you want to deal with warnings later
    ignoreDuringBuilds: false,
  },
};

export default nextConfig;