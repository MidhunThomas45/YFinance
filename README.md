# iMarketPredict Stock API

A FastAPI-based REST API for fetching real-time and historical stock data from Yahoo Finance using company ticker symbols. **No database required - all data is fetched directly from Yahoo Finance.**

## Features

- **Real-time Data**: Get latest stock prices and OHLCV data
- **Historical Data**: Fetch historical data with customizable periods and intervals
- **Company Information**: Retrieve company details, sector, market cap, etc.
- **Batch Operations**: Fetch data for multiple symbols simultaneously
- **No Database**: Works without any database setup or configuration
- **RESTful API**: Clean, documented endpoints for easy integration

## API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API information and available endpoints |
| `GET` | `/health` | Health check and API status |
| `GET` | `/symbols/suggested` | List of suggested popular stock symbols |

### Stock Data Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/stock/{symbol}/history` | Historical OHLCV data |
| `GET` | `/stock/{symbol}/latest` | Latest real-time data |
| `GET` | `/stock/{symbol}/info` | Company information |

### Utility Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/batch/{symbols}/history` | Batch historical data for multiple symbols |

## Setup Instructions

### 1. Prerequisites

- Python 3.8+
- Virtual environment (recommended)

### 2. Installation

```bash
# Clone the repository
git clone <repository-url>
cd yfinance

# Create virtual environment
python -m venv myvenv

# Activate virtual environment
# Windows
myvenv\Scripts\activate
# Linux/Mac
source myvenv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Run the Application

```bash
# Start the API server
python main.py

# Or use the startup script
python start_api.py
```

The API will be available at `http://localhost:8000`

## Usage Examples

### 1. Get Historical Data

```bash
# Get 1 year of daily data for Apple
curl "http://localhost:8000/stock/AAPL/history?period=1y&interval=1d"

# Get 5 days of hourly data for Tesla
curl "http://localhost:8000/stock/TSLA/history?period=5d&interval=1h"
```

### 2. Get Real-time Data

```bash
# Get latest data for Microsoft
curl "http://localhost:8000/stock/MSFT/latest"
```

### 3. Get Company Information

```bash
# Get company info for Google
curl "http://localhost:8000/stock/GOOGL/info"
```

### 4. Batch Operations

```bash
# Get data for multiple symbols
curl "http://localhost:8000/batch/AAPL,MSFT,GOOGL/history?period=1d&interval=1h"
```

## Postman Collection

Import this collection into Postman for easy testing:

```json
{
  "info": {
    "name": "iMarketPredict Stock API",
    "description": "API for fetching stock data from Yahoo Finance"
  },
  "item": [
    {
      "name": "Get API Info",
      "request": {
        "method": "GET",
        "url": "http://localhost:8000/"
      }
    },
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": "http://localhost:8000/health"
      }
    },
    {
      "name": "Get Stock History",
      "request": {
        "method": "GET",
        "url": "http://localhost:8000/stock/AAPL/history",
        "params": [
          {"key": "period", "value": "1y"},
          {"key": "interval", "value": "1d"},
          {"key": "limit", "value": "100"}
        ]
      }
    },
    {
      "name": "Get Latest Data",
      "request": {
        "method": "GET",
        "url": "http://localhost:8000/stock/AAPL/latest"
      }
    },
    {
      "name": "Get Company Info",
      "request": {
        "method": "GET",
        "url": "http://localhost:8000/stock/AAPL/info"
      }
    },
    {
      "name": "Batch History",
      "request": {
        "method": "GET",
        "url": "http://localhost:8000/batch/AAPL,MSFT,GOOGL/history",
        "params": [
          {"key": "period", "value": "5d"},
          {"key": "interval", "value": "1h"}
        ]
      }
    }
  ]
}
```

## Data Parameters

### Time Periods
- `1d` - 1 day
- `5d` - 5 days
- `1mo` - 1 month
- `3mo` - 3 months
- `6mo` - 6 months
- `1y` - 1 year
- `5y` - 5 years
- `10y` - 10 years
- `max` - Maximum available

### Intervals
- `1m` - 1 minute (limited to 7 days)
- `2m` - 2 minutes (limited to 60 days)
- `5m` - 5 minutes (limited to 60 days)
- `15m` - 15 minutes (limited to 60 days)
- `1h` - 1 hour (limited to 730 days)
- `1d` - 1 day

## Error Handling

The API includes comprehensive error handling:

- **400 Bad Request**: Invalid parameters or missing required fields
- **404 Not Found**: Symbol not found or no data available
- **500 Internal Server Error**: Server-side errors with detailed messages

## Logging

The application logs all operations to help with debugging:

- API requests and responses
- Yahoo Finance API calls
- Error details and stack traces

## Performance Considerations

- All data is fetched directly from Yahoo Finance in real-time
- No local caching or storage
- Batch operations are optimized for multiple symbols
- Rate limiting is handled by Yahoo Finance

## Troubleshooting

### Common Issues

1. **No Data Returned**
   - Verify ticker symbol is correct
   - Check if market is open (real-time data only available during trading hours)
   - Ensure internet connection is stable

2. **Rate Limiting**
   - Yahoo Finance may limit requests for very frequent calls
   - Wait a few seconds between requests

3. **API Not Starting**
   - Check if port 8000 is available
   - Verify all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version (3.8+ required)

### Debug Mode

Enable debug logging by setting the log level:

```bash
uvicorn main:app --log-level debug
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Check the logs for error details
- Verify your configuration
- Ensure all dependencies are installed correctly


#python start_api.py