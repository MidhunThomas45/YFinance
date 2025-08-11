# main.py
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from services.stock_service import (
    fetch_historical_ohlcv, 
    fetch_realtime_latest, 
    fetch_multiple_symbols,
    get_symbol_info
)
from services.storage_service import upsert_ohlcv_from_df, query_ohlcv, get_symbols_from_db
from jobs.fetch_jobs import start_scheduler, job_fetch_and_store
from db import create_tables, check_db_connection
from typing import Optional, List
import uvicorn
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="iMarketPredict Stock API",
    description="API for fetching real-time and historical stock data from Yahoo Finance",
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
    """Initialize database and start scheduler on app startup"""
    try:
        # Check database connection
        if check_db_connection():
            logger.info("Database connection successful")
            # Create tables if they don't exist
            create_tables()
            
            # Run initial data fetch
            try:
                job_fetch_and_store(DEFAULT_TICKERS, period="5d", interval="1h")
                logger.info("Initial data fetch completed")
            except Exception as e:
                logger.warning(f"Initial data fetch failed: {e}")
            
            # Start scheduler for daily updates
            start_scheduler(DEFAULT_TICKERS, cron_expr={"hour": 1, "minute": 0})
            logger.info("Scheduler started successfully")
        else:
            logger.error("Database connection failed - some features may not work")
    except Exception as e:
        logger.error(f"Startup error: {e}")

@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "message": "iMarketPredict Stock API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "health": "/health",
            "symbols": "/symbols",
            "stock_history": "/stock/{symbol}/history",
            "stock_latest": "/stock/{symbol}/latest",
            "stock_info": "/stock/{symbol}/info",
            "stock_db": "/stock/{symbol}/db",
            "trigger_fetch": "/trigger/fetch"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    db_status = check_db_connection()
    return {
        "status": "healthy" if db_status else "degraded",
        "database": "connected" if db_status else "disconnected",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/symbols")
def get_available_symbols():
    """Get list of available symbols from database"""
    try:
        symbols = get_symbols_from_db()
        return {
            "symbols": symbols,
            "count": len(symbols),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting symbols: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve symbols")

@app.get("/stock/{symbol}/history")
def get_history(
    symbol: str, 
    period: str = Query("1y", description="Time period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 5y, 10y, max"),
    interval: str = Query("1d", description="Data interval: 1m, 2m, 5m, 15m, 1h, 1d"),
    limit: Optional[int] = Query(1000, description="Maximum number of records to return"),
    store: bool = Query(True, description="Whether to store data in database")
):
    """Get historical OHLCV data for a symbol"""
    try:
        logger.info(f"Fetching history for {symbol} - period: {period}, interval: {interval}")
        
        df = fetch_historical_ohlcv(symbol, period=period, interval=interval)
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol}")
        
        # Store in database if requested
        if store:
            try:
                rows_inserted = upsert_ohlcv_from_df(df)
                logger.info(f"Stored {rows_inserted} rows for {symbol}")
            except Exception as e:
                logger.warning(f"Failed to store data for {symbol}: {e}")
        
        # Return data
        data = df.to_dict(orient="records")
        return {
            "symbol": symbol.upper(),
            "period": period,
            "interval": interval,
            "total_records": len(data),
            "rows": data[-limit:] if limit else data,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching history for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch data for {symbol}")

@app.get("/stock/{symbol}/latest")
def get_latest(symbol: str, store: bool = Query(True, description="Whether to store data in database")):
    """Get latest real-time data for a symbol"""
    try:
        logger.info(f"Fetching latest data for {symbol}")
        
        latest = fetch_realtime_latest(symbol)
        if not latest:
            raise HTTPException(status_code=404, detail=f"No real-time data found for symbol {symbol}")
        
        # Store in database if requested
        if store:
            try:
                import pandas as pd
                df = pd.DataFrame([{
                    "symbol": latest['symbol'],
                    "dt": pd.to_datetime(latest['dt']),
                    "open": latest['open'],
                    "high": latest['high'],
                    "low": latest['low'],
                    "close": latest['close'],
                    "volume": latest['volume']
                }])
                upsert_ohlcv_from_df(df)
            except Exception as e:
                logger.warning(f"Failed to store latest data for {symbol}: {e}")
        
        return {
            **latest,
            "timestamp": datetime.now().isoformat()
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
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching company info for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch company information for {symbol}")

@app.get("/stock/{symbol}/db")
def get_from_db(
    symbol: str, 
    limit: int = Query(100, description="Maximum number of records to return")
):
    """Get stored data from database for a symbol"""
    try:
        rows = query_ohlcv(symbol, limit=limit)
        if not rows:
            raise HTTPException(status_code=404, detail=f"No stored data found for symbol {symbol}")
        
        return {
            "symbol": symbol.upper(),
            "total_records": len(rows),
            "rows": rows,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying database for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to query database for {symbol}")

@app.post("/trigger/fetch")
def trigger_fetch(
    symbols: List[str], 
    period: str = Query("5d", description="Time period for data fetch"),
    interval: str = Query("1h", description="Data interval for fetch")
):
    """Trigger manual data fetch for specified symbols"""
    try:
        logger.info(f"Triggering fetch for symbols: {symbols}")
        
        if not symbols:
            raise HTTPException(status_code=400, detail="At least one symbol must be provided")
        
        # Validate symbols
        valid_symbols = [s.upper().strip() for s in symbols if s.strip()]
        if not valid_symbols:
            raise HTTPException(status_code=400, detail="No valid symbols provided")
        
        # Start fetch job
        job_fetch_and_store(valid_symbols, period=period, interval=interval)
        
        return {
            "status": "started",
            "symbols": valid_symbols,
            "period": period,
            "interval": interval,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering fetch: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to trigger fetch: {str(e)}")

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
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in batch history fetch: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch batch data: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )
