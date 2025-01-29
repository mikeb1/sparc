# API Reference

## Overview
This document details the specifications and usage of our RESTful API endpoints.

## Authentication

### API Key Authentication
Include your API key in all requests via the Authorization header:
```bash
Authorization: Bearer YOUR_API_KEY
```

### OAuth 2.0 Endpoints

#### Authorization Request
```
GET /oauth/authorize
```
Parameters:
- client_id (required)
- redirect_uri (required)
- scope (optional)
- state (recommended)

#### Token Exchange
```
POST /oauth/token
```
Parameters:
- grant_type (required)
- code (required)
- client_id (required)
- client_secret (required)
- redirect_uri (required)

## Request/Response Standards

### Headers
Required request headers:
```
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY
Accept: application/json
```

### Response Format
All responses follow this structure:
```json
{
  "status": "success|error",
  "data": {
    // Response payload
  },
  "meta": {
    "page": 1,
    "perPage": 25,
    "total": 100
  }
}
```

## Rate Limits

### Default Limits
- 1000 requests per minute per API key
- 10000 requests per hour per API key

### Headers
Rate limit information is returned in headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

### Exceeded Limits
When rate limited, receives 429 response with:
```json
{
  "status": "error",
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please try again in 60 seconds",
    "retryAfter": 60
  }
}
```

## Error Codes

### HTTP Status Codes
- 200: Success
- 201: Created
- 204: No Content
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 429: Too Many Requests
- 500: Internal Server Error

### Error Response Format
```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format"
      }
    ]
  }
}
```

### Common Error Codes
| Code | Description |
|------|-------------|
| VALIDATION_ERROR | Invalid input data |
| AUTHENTICATION_ERROR | Invalid credentials |
| AUTHORIZATION_ERROR | Insufficient permissions |
| RESOURCE_NOT_FOUND | Requested resource doesn't exist |
| RATE_LIMIT_EXCEEDED | Too many requests |
| INTERNAL_ERROR | Server-side error |

## API Endpoints

### Users

#### List Users
```
GET /v1/users
```
Query parameters:
- page (default: 1)
- perPage (default: 25)
- sortBy (default: "createdAt")
- sortOrder (default: "desc")

Response:
```json
{
  "status": "success",
  "data": [
    {
      "id": "123",
      "email": "user@example.com",
      "name": "John Doe",
      "createdAt": "2023-01-01T00:00:00Z"
    }
  ],
  "meta": {
    "page": 1,
    "perPage": 25,
    "total": 100
  }
}
```

#### Create User
```
POST /v1/users
```
Request body:
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "role": "user"
}
```

#### Get User
```
GET /v1/users/{id}
```

#### Update User
```
PUT /v1/users/{id}
```
Request body:
```json
{
  "name": "John Smith",
  "role": "admin"
}
```

#### Delete User
```
DELETE /v1/users/{id}
```

## Usage Examples

### Authentication
```python
import requests

API_KEY = 'your_api_key'
headers = {
    'Authorization': f'Bearer {API_KEY}',
    'Content-Type': 'application/json'
}

# List users
response = requests.get(
    'https://api.example.com/v1/users',
    headers=headers
)

# Create user
user_data = {
    'email': 'user@example.com',
    'name': 'John Doe',
    'role': 'user'
}
response = requests.post(
    'https://api.example.com/v1/users',
    headers=headers,
    json=user_data
)
```

### Pagination
```python
def fetch_all_users():
    users = []
    page = 1
    
    while True:
        response = requests.get(
            'https://api.example.com/v1/users',
            params={'page': page},
            headers=headers
        )
        data = response.json()
        
        if not data['data']:
            break
            
        users.extend(data['data'])
        page += 1
    
    return users
```

### Error Handling
```python
try:
    response = requests.post(
        'https://api.example.com/v1/users',
        headers=headers,
        json=user_data
    )
    response.raise_for_status()
    user = response.json()['data']
    
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
