# syntax = docker/dockerfile:1

# Adjust NODE_VERSION as desired
ARG NODE_VERSION=20.18.1
FROM node:${NODE_VERSION}-slim as base

LABEL fly_launch_runtime="Next.js"

# Next.js app lives here
WORKDIR /app

# Set production environment
ENV NODE_ENV="production"

# Set non-sensitive configuration
ENV MODEL_NAME=claude-3-sonnet-20240229
ENV NEXT_PUBLIC_MODEL_NAME=claude-3-sonnet-20240229
ENV DEFAULT_MODEL=anthropic
ENV NEXT_PUBLIC_ENABLE_SUPABASE=true
ENV NEXT_PUBLIC_SUPABASE_URL=https://eojucgnpskovtadfwfir.supabase.co

# Throw-away build stage to reduce size of final image
FROM base as build

# Install packages needed to build node modules
RUN apt-get update -qq && \
    apt-get install --no-install-recommends -y build-essential node-gyp pkg-config python-is-python3

# Install node modules
COPY package-lock.json package.json ./
RUN npm ci --include=dev

# Copy env file first
COPY .env .env

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

# Set non-sensitive configuration
ENV MODEL_NAME=claude-3-sonnet-20240229
ENV NEXT_PUBLIC_MODEL_NAME=claude-3-sonnet-20240229
ENV DEFAULT_MODEL=anthropic
ENV NEXT_PUBLIC_ENABLE_SUPABASE=true
ENV NEXT_PUBLIC_SUPABASE_URL=https://eojucgnpskovtadfwfir.supabase.co


# Start the server by default, this can be overwritten at runtime
EXPOSE 3000
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"
ENV NEXT_SHARP_PATH="/tmp/node_modules/sharp"
CMD [ "npm", "run", "start" ]
