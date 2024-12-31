/** @type {import('next').NextConfig} */
const nextConfig = {
  // Allow connections from any host
  experimental: {
    serverMinification: false,
  },
  env: {
    ANTHROPIC_API_KEY: process.env.ANTHROPIC_API_KEY,
    E2B_API_KEY: process.env.E2B_API_KEY,
    MODEL_NAME: process.env.MODEL_NAME,
    NEXT_PUBLIC_MODEL_NAME: process.env.NEXT_PUBLIC_MODEL_NAME,
    DEFAULT_MODEL: process.env.DEFAULT_MODEL,
    NEXT_PUBLIC_SITE_URL: process.env.NEXT_PUBLIC_SITE_URL,
    NEXT_PUBLIC_ENABLE_SUPABASE: process.env.NEXT_PUBLIC_ENABLE_SUPABASE,
    NEXT_PUBLIC_SUPABASE_URL: process.env.NEXT_PUBLIC_SUPABASE_URL,
    NEXT_PUBLIC_SUPABASE_ANON_KEY: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
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
