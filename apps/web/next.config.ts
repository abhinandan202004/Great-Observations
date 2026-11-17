import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Produces a self-contained server in .next/standalone for the container image.
  output: "standalone",
  cacheComponents: true,
  partialPrefetching: true,
  // The browser reaches the API through the web app, so no CORS setup is needed.
  // shortcut: API_URL is read at build time and fixed in the image;
  // proxy in a route handler instead if one image must serve several environments.
  rewrites: async () => [
    {
      source: "/api/:path*",
      destination: `${process.env.API_URL ?? "http://localhost:8000"}/:path*`,
    },
  ],
};

export default nextConfig;
