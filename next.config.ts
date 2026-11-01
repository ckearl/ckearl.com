import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async redirects() {
    return [{ source: "/new-design", destination: "/", permanent: true }];
  },
};

export default nextConfig;
