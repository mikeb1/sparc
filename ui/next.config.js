/** @type {import('next').NextConfig} */
const nextConfig = {
  // Allow connections from any host
  experimental: {
    serverMinification: false,
  },
  // Server configuration
  server: {
    port: parseInt(process.env.PORT) || 3000,
    host: process.env.HOSTNAME || '0.0.0.0',
  },
  webpack: (config, { isServer }) => {
    if (!isServer) {
      // Don't attempt to import node-specific modules on the client side
      config.resolve.fallback = {
        ...config.resolve.fallback,
        child_process: false,
        fs: false,
        net: false,
        tls: false
      }
    }
    return config
  }
}

export default nextConfig
