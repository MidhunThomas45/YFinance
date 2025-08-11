# iMarketPredict Stock API

A FastAPI-based REST API for fetching real-time and historical stock data from Yahoo Finance using company ticker symbols.

## Features

- **Real-time Data**: Get latest stock prices and OHLCV data
- **Historical Data**: Fetch historical data with customizable periods and intervals
- **Company Information**: Retrieve company details, sector, market cap, etc.
- **Database Storage**: Store and query historical data locally
- **Batch Operations**: Fetch data for multiple symbols simultaneously
- **Scheduled Updates**: Automatic daily data updates
- **RESTful API**: Clean, documented endpoints for easy integration

## API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API information and available endpoints |
| `GET` | `/health` | Health check and database status |
| `GET` | `/symbols` | List of available symbols in database |

### Stock Data Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/stock/{symbol}/history` | Historical OHLCV data |
| `GET` | `/stock/{symbol}/latest` | Latest real-time data |
| `GET` | `/stock/{symbol}/info` | Company information |
| `GET` | `/stock/{symbol}/db` | Stored data from database |

### Utility Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/trigger/fetch` | Manually trigger data fetch |
| `GET` | `/batch/{symbols}/history` | Batch historical data for multiple symbols |

## Setup Instructions

### 1. Prerequisites

- Python 3.8+
- MySQL/MariaDB database
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

### 3. Database Setup

```sql
-- Create database
CREATE DATABASE stock_data CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create user (optional)
CREATE USER 'stock_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON stock_data.* TO 'stock_user'@'localhost';
FLUSH PRIVILEGES;
```

### 4. Configuration

This project reads settings directly from OS environment variables via `os.getenv(...)`. It does not automatically load a `.env` file.

- Required: set `DATABASE_URL` or keep the default in `config.py` (`mysql://root:password@localhost:3306/stock_data`).
- Optional: `API_HOST`, `API_PORT`, `YF_TIMEOUT`, `YF_RETRIES`.

Windows PowerShell examples:

```powershell
$env:DATABASE_URL="mysql://root:password@localhost:3306/stock_data"
$env:API_HOST="0.0.0.0"
$env:API_PORT="8000"
```

Alternative (pure-Python) DBAPI using PyMySQL:

```bash
pip install pymysql
```

Then set (Windows PowerShell):

```powershell
$env:DATABASE_URL="mysql+pymysql://root:password@localhost:3306/stock_data"
```

### 5. Run the Application

```bash
# Easiest (includes preflight checks)
python start.py

# Or run the app module directly
python main.py

# Or use uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`.

Note: If you do not have a database configured, the API can still serve data from Yahoo Finance. Use `store=false` on endpoints to skip DB writes, e.g.:

```
GET /stock/AAPL/history?period=1y&interval=1d&store=false
```

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

### 5. Trigger Manual Fetch

```bash
# Trigger data fetch for specific symbols
curl -X POST "http://localhost:8000/trigger/fetch" \
     -H "Content-Type: application/json" \
     -d '{"symbols": ["AAPL", "MSFT"], "period": "5d", "interval": "1h"}'
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
- Database operations
- Yahoo Finance API calls
- Error details and stack traces

## Performance Considerations

- Data is cached in the database for faster subsequent requests
- Batch operations are optimized for multiple symbols
- Database indexes are created on frequently queried fields
- Connection pooling is used for database operations

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Check the `DATABASE_URL` environment variable or update the default in `config.py`
   - Ensure MySQL service is running
   - Verify database exists and user has permissions

2. **No Data Returned**
   - Verify ticker symbol is correct
   - Check if market is open (real-time data only available during trading hours)
   - Ensure internet connection is stable

3. **Rate Limiting**
   - Yahoo Finance may limit requests for very frequent calls
   - Use the database storage feature to reduce API calls

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
