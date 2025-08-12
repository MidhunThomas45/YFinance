# main.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from services.stock_service import (
    fetch_historical_ohlcv, 
    fetch_realtime_latest, 
    fetch_multiple_symbols,
    get_symbol_info
)
from typing import Optional, List
import uvicorn
import logging
from datetime import datetime
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="iMarketPredict Stock API",
    description="API for fetching real-time and historical stock data from Yahoo Finance - No Database Required",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Default ticker symbols
DEFAULT_TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX"]

@app.on_event("startup")
async def startup_event():
    """Initialize API on startup"""
    try:
        logger.info("Starting iMarketPredict Stock API...")
        logger.info("Database features disabled - running in read-only mode")
        logger.info("All data is fetched directly from Yahoo Finance")
        logger.info("API startup completed successfully")
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
        logger.info("API will continue to run but some features may be limited")

@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "message": "iMarketPredict Stock API",
        "version": "1.0.0",
        "status": "running",
        "database": "disabled",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "health": "/health",
            "stock_history": "/stock/{symbol}/history",
            "stock_latest": "/stock/{symbol}/latest",
            "stock_info": "/stock/{symbol}/info",
            "batch_history": "/batch/{symbols}/history"
        },
        "note": "This API fetches data directly from Yahoo Finance - no database storage"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "disabled",
        "timestamp": datetime.now().isoformat(),
        "message": "API is running successfully - fetching data from Yahoo Finance"
    }

@app.get("/stock/{symbol}/history")
def get_history(
    symbol: str, 
    period: str = Query("1d", description="Time period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 5y, 10y, max"),
    interval: str = Query("1d", description="Data interval: 1m, 2m, 5m, 15m, 1h, 1d"),
    limit: Optional[int] = Query(1000, description="Maximum number of records to return")
):
    """Get historical OHLCV data for a symbol"""
    try:
        logger.info(f"Fetching history for {symbol} - period: {period}, interval: {interval}")
        
        df = fetch_historical_ohlcv(symbol, period=period, interval=interval)
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol}")
        
        # Return data directly from Yahoo Finance
        data = df.to_dict(orient="records")
        return {
            "symbol": symbol.upper(),
            "period": period,
            "interval": interval,
            "total_records": len(data),
            "rows": data[-limit:] if limit else data,
            "timestamp": datetime.now().isoformat(),
            "source": "Yahoo Finance",
            "stored": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching history for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch data for {symbol}")

@app.get("/stock/{symbol}/latest")
def get_latest(symbol: str):
    """Get latest real-time data for a symbol"""
    try:
        logger.info(f"Fetching latest data for {symbol}")
        
        latest = fetch_realtime_latest(symbol)
        if not latest:
            raise HTTPException(status_code=404, detail=f"No real-time data found for symbol {symbol}")
        
        return {
            **latest,
            "timestamp": datetime.now().isoformat(),
            "source": "Yahoo Finance",
            "stored": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching latest data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch latest data for {symbol}")

@app.get("/stock/{symbol}/info")
def get_stock_info(symbol: str):
    """Get company information for a symbol"""
    try:
        logger.info(f"Fetching company info for {symbol}")
        
        info = get_symbol_info(symbol)
        if not info:
            raise HTTPException(status_code=404, detail=f"No company information found for symbol {symbol}")
        
        return {
            **info,
            "timestamp": datetime.now().isoformat(),
            "source": "Yahoo Finance"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching company info for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch company information for {symbol}")

@app.get("/batch/{symbols}/history")
def get_batch_history(
    symbols: str,
    period: str = Query("1d", description="Time period"),
    interval: str = Query("1h", description="Data interval")
):
    """Get historical data for multiple symbols (comma-separated)"""
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
        if not symbol_list:
            raise HTTPException(status_code=400, detail="No valid symbols provided")
        
        logger.info(f"Fetching batch history for symbols: {symbol_list}")
        
        results = fetch_multiple_symbols(symbol_list, period=period, interval=interval)
        
        if not results:
            raise HTTPException(status_code=404, detail="No data found for any of the specified symbols")
        
        # Convert to response format
        response_data = {}
        for symbol, df in results.items():
            response_data[symbol] = {
                "total_records": len(df),
                "rows": df.to_dict(orient="records")
            }
        
        return {
            "symbols": symbol_list,
            "period": period,
            "interval": interval,
            "data": response_data,
            "timestamp": datetime.now().isoformat(),
            "source": "Yahoo Finance"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch history fetch: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch batch data: {str(e)}")

@app.get("/symbols/suggested")
def get_suggested_symbols():
    """Get list of suggested popular stock symbols"""
    return {
        "suggested_symbols": DEFAULT_TICKERS,
        "count": len(DEFAULT_TICKERS),
        "timestamp": datetime.now().isoformat(),
        "note": "These are popular stock symbols you can test with"
    }

@app.get("/test")
def test_endpoint():
    """Simple test endpoint"""
    return {
        "message": "API is working!",
        "timestamp": datetime.now().isoformat(),
        "status": "success"
    }

if __name__ == "__main__":
    print("=" * 60)
    print("Starting iMarketPredict Stock API (No Database)")
    print("=" * 60)
    print("This API fetches data directly from Yahoo Finance")
    print("No database storage - all data is real-time")
    print("=" * 60)
    print("API will be available at: http://localhost:8000")
    print("Test endpoints:")
    print("  - http://localhost:8000/test")
    print("  - http://localhost:8000/health")
    print("  - http://localhost:8000/stock/AAPL/latest")
    print("  - http://localhost:8000/stock/AAPL/history")
    print("  - http://localhost:8000/batch/AAPL,MSFT,GOOGL/history")
    print("=" * 60)
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Check if running on Windows and disable reload if needed
    is_windows = os.name == 'nt'
    
    try:
        if is_windows:
            print("Running on Windows - disabling reload feature for stability")
            uvicorn.run(
                "main:app", 
                host="0.0.0.0", 
                port=8000,  # Back to original port 8000
                reload=False,  # Disable reload on Windows
                log_level="info"
            )
        else:
            uvicorn.run(
                "main:app", 
                host="0.0.0.0", 
                port=8000,  # Back to original port 8000
                reload=True,
                log_level="info"
            )
    except Exception as e:
        print(f"Error starting server: {e}")
        print("Trying without reload feature...")
        try:
            uvicorn.run(
                "main:app", 
                host="0.0.0.0", 
                port=8000,  # Back to original port 8000
                reload=False,
                log_level="info"
            )
        except Exception as e2:
            print(f"Failed to start server: {e2}")
            print("Please check if port 8000 is available and try again.")
