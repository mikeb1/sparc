#!/bin/bash

# Exit on error
set -e

# Copy env.local to .env
echo "Copying env.local to .env..."
cp env.local .env

echo "Setting Fly.io secrets from env.local..."

# Read env.local and set each non-empty value as a secret
while IFS='=' read -r key value; do
    # Skip comments and empty lines
    [[ $key =~ ^#.*$ ]] || [ -z "$key" ] && continue
    
    # Trim whitespace
    key=$(echo $key | xargs)
    value=$(echo $value | xargs)
    
    # Only set if value is not empty
    if [ ! -z "$value" ]; then
        echo "Setting $key"
        flyctl secrets set "$key=$value"
    fi
done < env.local

# Validate API key format
API_KEY=$(grep "^ANTHROPIC_API_KEY=" env.local | cut -d '=' -f2 | xargs)

if [ -z "$API_KEY" ]; then
    echo "Error: ANTHROPIC_API_KEY not found in env.local"
    exit 1
fi

if [[ ! "$API_KEY" =~ ^sk-ant-api ]]; then
    echo "Error: Invalid ANTHROPIC_API_KEY format - should start with sk-ant-api"
    exit 1
fi

echo "API key validation successful"
echo "Deploying application..."
flyctl deploy

echo "Deployment complete!"
