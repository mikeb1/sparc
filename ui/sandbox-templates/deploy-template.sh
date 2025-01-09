#!/bin/bash

# Function to sanitize name (replace spaces with hyphens)
sanitize_name() {
    echo "$1" | tr ' ' '-' | tr -cd '[:alnum:]-'
}

# Function to create .env if it doesn't exist
setup_env() {
    if [ ! -f ".env" ]; then
        echo "Creating .env file..."
        touch .env
        echo "# Add your environment variables here" > .env
        echo "ANTHROPIC_API_KEY=" >> .env
    fi
}

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | xargs)
fi

# Check for Anthropic API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "Warning: ANTHROPIC_API_KEY not found in .env"
    echo "Please add it to continue"
    exit 1
fi

# Prompt for template name
echo "Enter template name (no spaces):"
read template_name

# Sanitize template name
template_name=$(sanitize_name "$template_name")
echo "Using template name: $template_name"

# Create template directory
template_dir="./$template_name"
if [ -d "$template_dir" ]; then
    echo "Error: Template directory already exists"
    exit 1
fi

# Prompt for description
echo "Enter template description:"
read template_description

# Create template directory and initialize e2b template
mkdir -p "$template_dir"
cd "$template_dir" || exit

# Initialize e2b template
echo "Initializing e2b template..."
if ! e2b template init; then
    echo "Error: Failed to initialize e2b template"
    cd ..
    rm -rf "$template_dir"
    exit 1
fi

# Generate Dockerfile using Anthropic
echo "Generating e2b.Dockerfile..."
dockerfile_response=$(curl -X POST "https://api.anthropic.com/v1/messages" \
    -H "Content-Type: application/json" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -d "{\"model\":\"claude-3-sonnet-20240229\",\"max_tokens\":1024,\"messages\":[{\"role\":\"user\",\"content\":\"You are creating a specialized e2b.Dockerfile for a template named '$template_name' with purpose: '$template_description'. Analyze the name and purpose to determine the most relevant Python packages needed. For example, a data science template needs pandas/numpy/scikit-learn, a testing template needs pytest/coverage, a web template needs flask/requests. Generate a Dockerfile that starts with 'FROM e2bdev/code-interpreter:latest' followed by a single RUN pip install command with all needed packages for this specific use case. No COPY, no requirements.txt, no comments. Output only the Dockerfile content.\"}]}")

# Extract Dockerfile content and installed packages
echo "$dockerfile_response" | jq -r '.content[0].text' > e2b.Dockerfile
installed_packages=$(grep "pip install" e2b.Dockerfile | sed 's/.*pip install --no-cache-dir //')

# Build template
echo "Building template..."
if ! e2b template build; then
    echo "Error: Failed to build template"
    cd ..
    rm -rf "$template_dir"
    exit 1
fi

# Wait for e2b.toml to be created
max_attempts=5
attempt=1
while [ ! -f "e2b.toml" ] && [ $attempt -le $max_attempts ]; do
    echo "Waiting for e2b.toml to be created - try $attempt of $max_attempts..."
    sleep 2
    attempt=$((attempt + 1))
done

if [ ! -f "e2b.toml" ]; then
    echo "Error: e2b.toml not found after build"
    cd ..
    rm -rf "$template_dir"
    exit 1
fi

# Update e2b.toml with template name
sed -i "s/template_name = .*/template_name = \"$template_name\"/" e2b.toml

# Extract template ID from e2b.toml
template_id=$(grep "template_id" e2b.toml | cut -d'"' -f2)
if [ -z "$template_id" ]; then
    echo "Error: Could not extract template ID from e2b.toml"
    exit 1
fi

# Generate test.py using Anthropic
echo "Generating test.py..."
curl -X POST "https://api.anthropic.com/v1/messages" \
    -H "Content-Type: application/json" \
    -H "x-api-key: $ANTHROPIC_API_KEY" \
    -H "anthropic-version: 2023-06-01" \
    -d "{\"model\":\"claude-3-sonnet-20240229\",\"max_tokens\":1024,\"messages\":[{\"role\":\"user\",\"content\":\"Write a Python script that validates the $template_name template ($template_description). Use template_id='$template_id'. The sandbox has these packages installed: $installed_packages. Create a script that: 1) Imports e2b_code_interpreter, 2) Creates a sandbox with the template ID, 3) Runs test code that uses the installed packages to validate the template works as intended. The response should ONLY contain valid Python code without any markdown or comments.\"}]}" | jq -r '.content[0].text' > test.py

echo "Template created successfully at $template_dir"
echo "Template ID: $template_id"
echo "You can now:"
echo "1. Customize the e2b.Dockerfile as needed"
echo "2. Run test.py to validate the sandbox"
