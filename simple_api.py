#!/usr/bin/env python3
"""
Very Simple Stock API - Minimal dependencies
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from datetime import datetime
import requests
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Simple Stock API",
    description="Basic API for testing - fetches data from Yahoo Finance",
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
    """Root endpoint"""
    return {
        "message": "Simple Stock API is running!",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "test": "/test",
            "health": "/health",
            "stock_data": "/stock/{symbol}",
            "stock_info": "/stock/{symbol}/info"
        }
    }

@app.get("/test")
def test_endpoint():
    """Simple test endpoint"""
    return {
        "message": "API is working!",
        "timestamp": datetime.now().isoformat(),
        "status": "success"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "message": "API is running successfully"
    }

@app.get("/stock/{symbol}")
def get_stock_data(symbol: str):
    """Get basic stock data for a symbol"""
    try:
        logger.info(f"Fetching data for {symbol}")
        
        # Simple data response for testing
        return {
            "symbol": symbol.upper(),
            "message": f"Data request received for {symbol}",
            "timestamp": datetime.now().isoformat(),
            "note": "This is a test endpoint. Real data fetching will be added next."
        }
        
    except Exception as e:
        logger.error(f"Error processing request for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process request for {symbol}")

@app.get("/stock/{symbol}/info")
def get_stock_info(symbol: str):
    """Get company information for a symbol"""
    try:
        logger.info(f"Fetching company info for {symbol}")
        
        # Simple info response for testing
        return {
            "symbol": symbol.upper(),
            "company_name": f"Company {symbol}",
            "sector": "Technology",
            "industry": "Software",
            "timestamp": datetime.now().isoformat(),
            "note": "This is a test endpoint. Real company data will be added next."
        }
        
    except Exception as e:
        logger.error(f"Error fetching company info for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch company information for {symbol}")

@app.get("/ping")
def ping():
    """Simple ping endpoint"""
    return {"pong": True, "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    print("=" * 50)
    print("Starting Simple Stock API...")
    print("=" * 50)
    print("API will be available at: http://localhost:8000")
    print("Test endpoints:")
    print("  - http://localhost:8000/test")
    print("  - http://localhost:8000/health")
    print("  - http://localhost:8000/ping")
    print("  - http://localhost:8000/stock/AAPL")
    print("=" * 50)
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    uvicorn.run(
        "simple_api:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )
