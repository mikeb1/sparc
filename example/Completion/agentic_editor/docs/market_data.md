# Market Data Provider Documentation

## Interface

The `AbstractMarketDataProvider` interface defines the standard contract for market data providers:

```python
class AbstractMarketDataProvider:
    def get_current_price(self, symbol: str) -> float
    def get_historical_data(self, symbol: str, start_date: datetime, end_date: datetime) -> List[Dict]
    def subscribe_to_updates(self, symbol: str, callback: Callable[[PriceUpdate], None]) -> None
    def unsubscribe(self, symbol: str) -> None
```

## Available Implementations

### SimpleMarketDataProvider
A basic implementation providing simulated market data:

- Maintains in-memory price cache
- Generates synthetic historical data
- Simulates price updates using random walk
- Supports real-time price subscriptions

Configuration:
```python
provider = SimpleMarketDataProvider()
```

### Data Update Frequency
- Real-time price updates: Every 1 second
- Historical data: Daily OHLCV bars
- Cache refresh: On-demand

## Usage Examples

### Getting Current Prices
```python
provider = SimpleMarketDataProvider()
price = provider.get_current_price("AAPL")
```

### Historical Data
```python
history = provider.get_historical_data(
    symbol="AAPL",
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 1, 9)
)
```

### Price Updates Subscription
```python
def price_callback(update: PriceUpdate):
    print(f"{update.symbol}: {update.price}")

provider.subscribe_to_updates("AAPL", price_callback)
```

## Caching Behavior

- Current prices cached in memory
- Historical data cached after first request
- Cache invalidation: Manual via provider restart
- No persistent storage

## Error Handling

The provider throws standard exceptions:
- KeyError: Unknown symbol
- ValueError: Invalid date range
- RuntimeError: Provider connection issues

## Best Practices

1. Unsubscribe when done with real-time updates
2. Use date ranges within reasonable bounds
3. Handle provider exceptions gracefully
4. Monitor callback performance
