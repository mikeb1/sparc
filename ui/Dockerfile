# syntax = docker/dockerfile:1

# Adjust NODE_VERSION as desired
ARG NODE_VERSION=20.18.1
FROM node:${NODE_VERSION}-slim as base

LABEL fly_launch_runtime="Next.js"

# Next.js app lives here
WORKDIR /app

# Set production environment
ENV NODE_ENV="production"

# Throw-away build stage to reduce size of final image
FROM base as build

# Accept build arguments for sensitive data
ARG NEXT_PUBLIC_SUPABASE_ANON_KEY
ARG ANTHROPIC_API_KEY
ARG E2B_API_KEY

# Make environment variables available during build
ENV ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY
ENV E2B_API_KEY=$E2B_API_KEY
ENV NEXT_PUBLIC_SUPABASE_ANON_KEY=$NEXT_PUBLIC_SUPABASE_ANON_KEY

# Install packages needed to build node modules
RUN apt-get update -qq && \
    apt-get install --no-install-recommends -y build-essential node-gyp pkg-config python-is-python3

# Install node modules
COPY package-lock.json package.json ./
RUN npm ci --include=dev

# Copy application code
COPY . .

# Build application
RUN npm run build

# Remove development dependencies
RUN npm prune --omit=dev


# Final stage for app image
FROM base

# Copy built application
COPY --from=build /app /app

# Set runtime environment variables
ENV MODEL_NAME=claude-3-sonnet-20240229 \
    NEXT_PUBLIC_MODEL_NAME=claude-3-sonnet-20240229 \
    DEFAULT_MODEL=anthropic \
    NEXT_PUBLIC_ENABLE_SUPABASE=true \
    NEXT_PUBLIC_SUPABASE_URL=https://eojucgnpskovtadfwfir.supabase.co \
    PORT=3000 \
    HOSTNAME="0.0.0.0" \
    NEXT_SHARP_PATH="/tmp/node_modules/sharp" \
    ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
    E2B_API_KEY=$E2B_API_KEY \
    NEXT_PUBLIC_SUPABASE_ANON_KEY=$NEXT_PUBLIC_SUPABASE_ANON_KEY

# Start the server by default, this can be overwritten at runtime
EXPOSE 3000
CMD [ "npm", "run", "start" ]
