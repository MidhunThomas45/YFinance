#!/usr/bin/env python3
"""
Simple test API for iMarketPredict Stock API - works without database
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
from typing import Optional
import uvicorn
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="iMarketPredict Stock API (Test Version)",
    description="Simple API for fetching stock data from Yahoo Finance - No Database Required",
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

@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "message": "iMarketPredict Stock API (Test Version)",
        "version": "1.0.0",
        "status": "running",
        "database": "disabled",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "health": "/health",
            "stock_history": "/stock/{symbol}/history",
            "stock_latest": "/stock/{symbol}/latest",
            "stock_info": "/stock/{symbol}/info"
        },
        "note": "This is a test version that works without database"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "disabled",
        "timestamp": datetime.now().isoformat(),
        "message": "API is running in test mode without database"
    }

@app.get("/stock/{symbol}/history")
def get_history(
    symbol: str, 
    period: str = "1d",
    interval: str = "1h",
    limit: Optional[int] = 100
):
    """Get historical OHLCV data for a symbol"""
    try:
        logger.info(f"Fetching history for {symbol} - period: {period}, interval: {interval}")
        
        # Fetch data from Yahoo Finance
        df = yf.download(
            symbol, 
            period=period, 
            interval=interval, 
            auto_adjust=False, 
            progress=False,
            timeout=30
        )
        
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol}")
        
        # Process the data
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']].reset_index()
        df.columns = ['dt', 'open', 'high', 'low', 'close', 'volume']
        df['symbol'] = symbol.upper()
        
        # Clean data
        df = df.dropna()
        
        # Convert to response format
        data = df.to_dict(orient="records")
        
        return {
            "symbol": symbol.upper(),
            "period": period,
            "interval": interval,
            "total_records": len(data),
            "rows": data[-limit:] if limit else data,
            "timestamp": datetime.now().isoformat(),
            "stored": False
        }
        
    except Exception as e:
        logger.error(f"Error fetching history for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch data for {symbol}: {str(e)}")

@app.get("/stock/{symbol}/latest")
def get_latest(symbol: str):
    """Get latest real-time data for a symbol"""
    try:
        logger.info(f"Fetching latest data for {symbol}")
        
        # Get latest data
        df = yf.download(symbol, period="1d", interval="1m", auto_adjust=False, progress=False)
        
        if df.empty:
            raise HTTPException(status_code=404, detail=f"No real-time data found for symbol {symbol}")
        
        latest = df.tail(1).iloc[0]
        
        # Get additional info
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
        except:
            info = {}
        
        result = {
            "symbol": symbol.upper(),
            "dt": latest.name.strftime("%Y-%m-%d %H:%M:%S"),
            "open": float(latest['Open']),
            "high": float(latest['High']),
            "low": float(latest['Low']),
            "close": float(latest['Close']),
            "volume": float(latest['Volume']),
            "company_name": info.get('longName', ''),
            "sector": info.get('sector', ''),
            "market_cap": info.get('marketCap', ''),
            "currency": info.get('currency', 'USD'),
            "exchange": info.get('exchange', ''),
            "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return {
            **result,
            "timestamp": datetime.now().isoformat(),
            "stored": False
        }
        
    except Exception as e:
        logger.error(f"Error fetching latest data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch latest data for {symbol}: {str(e)}")

@app.get("/stock/{symbol}/info")
def get_stock_info(symbol: str):
    """Get company information for a symbol"""
    try:
        logger.info(f"Fetching company info for {symbol}")
        
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        if not info:
            raise HTTPException(status_code=404, detail=f"No company information found for symbol {symbol}")
        
        result = {
            "symbol": symbol.upper(),
            "company_name": info.get('longName', ''),
            "sector": info.get('sector', ''),
            "industry": info.get('industry', ''),
            "market_cap": info.get('marketCap', ''),
            "currency": info.get('currency', 'USD'),
            "exchange": info.get('exchange', ''),
            "country": info.get('country', ''),
            "website": info.get('website', ''),
            "description": info.get('longBusinessSummary', '')
        }
        
        return {
            **result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching company info for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch company information for {symbol}: {str(e)}")

@app.get("/test")
def test_endpoint():
    """Simple test endpoint"""
    return {
        "message": "API is working!",
        "timestamp": datetime.now().isoformat(),
        "status": "success"
    }

if __name__ == "__main__":
    print("Starting iMarketPredict Stock API (Test Version)...")
    print("This version works without database requirements")
    print("API will be available at: http://localhost:8000")
    print("Test endpoint: http://localhost:8000/test")
    print("Stock data: http://localhost:8000/stock/AAPL/latest")
    print("\nPress Ctrl+C to stop the server")
    
    uvicorn.run(
        "test_api:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )
