/** @type {import('next').NextConfig} */
const nextConfig = {
  webpack: (config) => {
    config.resolve.fallback = {
      ...config.resolve.fallback,
      path: false, // Ensure "path" module is not bundled
    };
    return config;
  },
};

export default nextConfig;
