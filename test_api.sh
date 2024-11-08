#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Testing Capitol AI API..."

# API configuration
API_ENDPOINT="https://api.capitol.ai/chat/async"
DOMAIN="https://aigrants.co/"
API_KEY="1tNHcGMBXaUxcicZmNF0aKnyEX/IcRWXr3xS96VMMmI="

# Make the API request
response=$(curl --location "$API_ENDPOINT" \
  --header "X-Domain: $DOMAIN" \
  --header "X-API-Key: $API_KEY" \
  --header "X-User-ID: 1" \
  --header "Content-Type: application/json" \
  --write-out "%{http_code}" \
  --silent \
  --output /dev/null \
  --data '{
    "story-id": "5d9c6076-f2fd-44a8-9ca1-de4014ff6299",
    "user_config_params": {
        "format": "custom",
        "cot": true,
        "audience": "General",
        "responseLength": "",
        "responseLanguage": "english",
        "heroImage": false,
        "title": false,
        "headers": true,
        "paragraphs": true,
        "images": false,
        "aiImages": false,
        "imageStyle": "auto",
        "aiGraphs": false,
        "webGraphs": false,
        "metrics": false,
        "tables": false,
        "quotes": false,
        "tweets": false,
        "tweetCharacterLimit": 280,
        "generalWebSearch": false,
        "academicWebSearch": false,
        "usePerplexity": false,
        "ragBudget": "default",
        "userQuery": "Use the provided grantee profile to write a grant volume according to additional instructions.",
        "customInstructions": "Please create a Technical Proposal demonstrating your capability to implement the grant project.",
        "imageHeight": 768,
        "imageWidth": 1344,
        "responseModel": "claude-3-5-sonnet-20240620",
        "userUrls": [
            "https://gist.github.com/zstone-cai/323e78d0b0e0f9f312105d2c1595bcbd"
        ],
        "userPdfDocuments": [],
        "userPdfUrls": [],
        "userImages": []
    }
}')

# Check HTTP status code
if [ "$response" -eq 200 ] || [ "$response" -eq 201 ]; then
    echo -e "${GREEN}Success!${NC} API request completed with status code: $response"
else
    echo -e "${RED}Error!${NC} API request failed with status code: $response"
fi
