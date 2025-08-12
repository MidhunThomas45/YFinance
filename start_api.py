#!/usr/bin/env python3
"""
Simple startup script for iMarketPredict Stock API
"""
import uvicorn
import os
import sys

def main():
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
    
    # Always disable reload for stability
    try:
        uvicorn.run(
            "main:app", 
            host="0.0.0.0", 
            port=8000,  # Back to original port 8000
            reload=False,  # Disable reload for stability
            log_level="info"
        )
    except Exception as e:
        print(f"Error starting server: {e}")
        print("Please check if port 8000 is available and try again.")
        print("You can also try running: uvicorn main:app --host 0.0.0.0 --port 8000")

if __name__ == "__main__":
    main()
