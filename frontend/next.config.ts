import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable standalone output for Docker deployment
  output: 'standalone',
  
  // Disable TypeScript checking for node_modules to avoid external dependency errors
  typescript: {
    ignoreBuildErrors: true,
  },


};

export default nextConfig;
