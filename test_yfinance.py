#!/usr/bin/env python3
"""
Simple test script to debug yfinance connectivity
"""
import yfinance as yf
import pandas as pd
import sys

def test_yfinance():
    print("=" * 50)
    print("Testing yfinance connectivity...")
    print("=" * 50)
    
    # Test 1: Basic download
    print("\n1. Testing basic download...")
    try:
        df = yf.download("AAPL", period="1d", interval="1h", progress=False)
        print(f"✓ Download successful! Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        if not df.empty:
            print(f"First row: {df.head(1)}")
        else:
            print("⚠ DataFrame is empty")
    except Exception as e:
        print(f"✗ Download failed: {e}")
    
    # Test 2: Ticker object
    print("\n2. Testing Ticker object...")
    try:
        ticker = yf.Ticker("AAPL")
        info = ticker.info
        print(f"✓ Ticker info successful!")
        print(f"Company: {info.get('longName', 'N/A')}")
        print(f"Sector: {info.get('sector', 'N/A')}")
    except Exception as e:
        print(f"✗ Ticker failed: {e}")
    
    # Test 3: Different period
    print("\n3. Testing different period...")
    try:
        df = yf.download("AAPL", period="5d", interval="1d", progress=False)
        print(f"✓ 5-day download successful! Shape: {df.shape}")
        if not df.empty:
            print(f"Date range: {df.index[0]} to {df.index[-1]}")
        else:
            print("⚠ DataFrame is empty")
    except Exception as e:
        print(f"✗ 5-day download failed: {e}")
    
    # Test 4: Check yfinance version
    print(f"\n4. yfinance version: {yf.__version__}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_yfinance()
