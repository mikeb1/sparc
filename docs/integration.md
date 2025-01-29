# API Integration Guide

## Overview
This guide covers key patterns and best practices for integrating with our RESTful API.

## Authentication
### API Keys
Authentication is handled via API keys passed in the HTTP Authorization header:

```bash
Authorization: Bearer YOUR_API_KEY
```

### OAuth 2.0
For applications requiring delegated user access, we support OAuth 2.0:

1. Redirect users to `/oauth/authorize`
2. Exchange authorization code for access token at `/oauth/token`
3. Use access token in Authorization header

## Data Formats
### Request Format
- Content-Type: application/json
- UTF-8 encoded
- Camel case field names

Example request:
```json
{
  "userId": "123",
  "orderItems": [
    {
      "productId": "456",
      "quantity": 2
    }
  ]
}
```

### Response Format
All responses follow a standard envelope:

```json
{
  "status": "success",
  "data": {
    // Response payload
  },
  "meta": {
    "page": 1,
    "totalPages": 10
  }
}
```

## Error Handling
### Error Response Format
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input provided",
    "details": [
      {
        "field": "email",
        "message": "Must be a valid email address"
      }
    ]
  }
}
```

### Common Error Codes
- 400 Bad Request - Invalid input
- 401 Unauthorized - Missing/invalid credentials
- 403 Forbidden - Valid credentials but insufficient permissions
- 404 Not Found - Resource doesn't exist
- 429 Too Many Requests - Rate limit exceeded
- 500 Internal Server Error - Server-side error

## Rate Limiting
Rate limits are applied per API key and enforced using a sliding window:

- 1000 requests per minute
- 10000 requests per hour

Rate limit info is included in response headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

### Handling Rate Limits
- Monitor X-RateLimit-* headers
- Implement exponential backoff when limits are reached
- Use bulk endpoints for high-volume operations

## Integration Examples

### Authentication
```python
import requests

API_KEY = 'your_api_key'
headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

response = requests.get('https://api.example.com/v1/users', headers=headers)
```

### Pagination
```python
def fetch_all_items():
    page = 1
    items = []
    
    while True:
        response = requests.get(
            'https://api.example.com/v1/items',
            params={'page': page},
            headers=headers
        )
        data = response.json()
        
        if not data['data']:
            break
            
        items.extend(data['data'])
        page += 1
    
    return items
```

### Error Handling
```python
try:
    response = requests.post(
        'https://api.example.com/v1/orders',
        headers=headers,
        json=order_data
    )
    response.raise_for_status()
    
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 429:
        # Handle rate limiting
        retry_after = int(e.response.headers.get('Retry-After', 60))
        time.sleep(retry_after)
    else:
        # Handle other errors
        error_data = e.response.json()
        print(f"API Error: {error_data['error']['message']}")
```

### Bulk Operations
```python
def bulk_create_users(users):
    # Split into chunks to stay within rate limits
    chunk_size = 100
    for i in range(0, len(users), chunk_size):
        chunk = users[i:i + chunk_size]
        response = requests.post(
            'https://api.example.com/v1/users/bulk',
            headers=headers,
            json={'users': chunk}
        )
        response.raise_for_status()
```
