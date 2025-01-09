#!/bin/bash

# Exit on error
set -e

echo "Reading environment variables from env.local..."

# Extract required keys from env.local
SUPABASE_KEY=$(grep "^NEXT_PUBLIC_SUPABASE_ANON_KEY=" env.local | cut -d '=' -f2 | xargs)
API_KEY=$(grep "^ANTHROPIC_API_KEY=" env.local | cut -d '=' -f2 | xargs)
E2B_KEY=$(grep "^E2B_API_KEY=" env.local | cut -d '=' -f2 | xargs)

# Validate required variables
if [ -z "$SUPABASE_KEY" ]; then
    echo "Error: NEXT_PUBLIC_SUPABASE_ANON_KEY not found in env.local"
    exit 1
fi

if [ -z "$API_KEY" ]; then
    echo "Error: ANTHROPIC_API_KEY not found in env.local"
    exit 1
fi

if [ -z "$E2B_KEY" ]; then
    echo "Error: E2B_API_KEY not found in env.local"
    exit 1
fi

if [[ ! "$API_KEY" =~ ^sk-ant-api ]]; then
    echo "Error: Invalid ANTHROPIC_API_KEY format - should start with sk-ant-api"
    exit 1
fi

# Set all secrets at once
echo "Setting Fly.io secrets..."
flyctl secrets set \
  NEXT_PUBLIC_SITE_URL="https://sparc-ui.fly.dev" \
  ANTHROPIC_API_KEY="$API_KEY" \
  E2B_API_KEY="$E2B_KEY" \
  NEXT_PUBLIC_SUPABASE_ANON_KEY="$SUPABASE_KEY"

echo "API key validation successful"
echo "Deploying application..."
flyctl deploy \
  --build-arg NEXT_PUBLIC_SUPABASE_ANON_KEY="$SUPABASE_KEY" \
  --build-arg ANTHROPIC_API_KEY="$API_KEY" \
  --build-arg E2B_API_KEY="$E2B_KEY"

echo "Deployment complete!"
