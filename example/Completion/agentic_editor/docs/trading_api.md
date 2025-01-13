# Trading API Documentation

## Authentication
All endpoints require an API key passed in the Authorization header:
```
Authorization: Bearer <api_key>
```

## Endpoints

### Orders

#### POST /api/orders
Create a new trading order.

Request body:
```json
{
  "portfolio_id": 123,
  "type": "buy",
  "symbol": "AAPL", 
  "quantity": 100,
  "price": 150.50
}
```

Response:
```json
{
  "id": 456,
  "status": "pending",
  "type": "buy",
  "symbol": "AAPL",
  "quantity": 100,
  "price": 150.50,
  "timestamp": "2024-01-09T10:30:00Z"
}
```

#### GET /api/orders/{order_id}
Get order details.

Response:
```json
{
  "id": 456,
  "status": "filled",
  "type": "buy",
  "symbol": "AAPL",
  "quantity": 100,
  "price": 150.50,
  "timestamp": "2024-01-09T10:30:00Z"
}
```

### Positions

#### GET /api/positions
Get all positions for a portfolio.

Query parameters:
- portfolio_id (required): Portfolio ID

Response:
```json
{
  "positions": [
    {
      "symbol": "AAPL",
      "quantity": 100,
      "entry_price": 150.50,
      "current_value": 15500
    }
  ]
}
```

### Portfolio

#### GET /api/portfolio/{portfolio_id}
Get portfolio details and metrics.

Response:
```json
{
  "id": 123,
  "total_value": 100000,
  "cash_balance": 25000,
  "positions": [...],
  "metrics": {
    "concentration_risk": 0.15,
    "largest_position_pct": 25.5
  }
}
```

## Error Handling

All endpoints return standard HTTP status codes:

- 200: Success
- 400: Bad request (invalid parameters)
- 401: Unauthorized (invalid/missing API key)
- 404: Resource not found
- 500: Internal server error

Error response format:
```json
{
  "error": {
    "code": "invalid_order",
    "message": "Invalid order parameters"
  }
}
```

## Rate Limits
- Maximum 100 requests per minute per API key
- Order creation limited to 10 per minute
