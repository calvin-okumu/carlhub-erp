import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enable standalone output for Docker deployment
  output: 'standalone',

  async rewrites() {
    // Only use rewrites in development when API is on localhost
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

    // Only rewrite if API is on localhost (development)
    if (apiUrl.includes('127.0.0.1') || apiUrl.includes('localhost')) {
      return [
        {
          source: '/api/:path*',
          destination: `${apiUrl}/api/:path*`,
        },
      ];
    }

    // In production, don't use rewrites - let the API calls go to the configured URL
    return [];
  },
};

export default nextConfig;
