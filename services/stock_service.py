# services/stock_service.py
import yfinance as yf
import pandas as pd
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)

def fetch_historical_ohlcv(symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    """
    Fetch historical OHLCV data using yfinance.
    period: '1d','5d','1mo','3mo','6mo','1y','5y','10y','max'
    interval: '1m','2m','5m','15m','1h','1d'
    Note: intervals shorter than '1d' are limited to recent history (30 days) for minute data.
    """
    try:
        logger.info(f"Fetching historical data for {symbol} - period: {period}, interval: {interval}")
        
        # Download data with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                df = yf.download(
                    symbol, 
                    period=period, 
                    interval=interval, 
                    auto_adjust=False, 
                    progress=False,
                    timeout=30
                )
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Failed to fetch data for {symbol} after {max_retries} attempts: {e}")
                    return pd.DataFrame()
                logger.warning(f"Attempt {attempt + 1} failed for {symbol}, retrying...")
                time.sleep(2 ** attempt)  # Exponential backoff
        
        if df.empty:
            logger.warning(f"No data returned for {symbol}")
            return pd.DataFrame()
        
        # Keep needed columns and reset index
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']].reset_index()
        df.columns = ['dt', 'open', 'high', 'low', 'close', 'volume']
        df['symbol'] = symbol.upper()
        
        # Clean data - remove rows with NaN values
        df = df.dropna()
        
        # Ensure proper data types
        df['open'] = pd.to_numeric(df['open'], errors='coerce')
        df['high'] = pd.to_numeric(df['high'], errors='coerce')
        df['low'] = pd.to_numeric(df['low'], errors='coerce')
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
        
        # Remove any remaining NaN rows
        df = df.dropna()
        
        logger.info(f"Successfully fetched {len(df)} records for {symbol}")
        return df[['symbol', 'dt', 'open', 'high', 'low', 'close', 'volume']]
        
    except Exception as e:
        logger.error(f"Error fetching historical data for {symbol}: {e}")
        return pd.DataFrame()

def fetch_realtime_latest(symbol: str, period: str = "1d", interval: str = "1m") -> Dict[str, Any]:
    """
    Get the latest available minute candle for today (near real-time).
    """
    try:
        df = fetch_historical_ohlcv(symbol, period=period, interval=interval)
        if df.empty:
            logger.warning(f"No real-time data available for {symbol}")
            return {}
        
        latest = df.tail(1).iloc[0]
        
        # Get additional info from yfinance
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        result = {
            "symbol": latest['symbol'],
            "dt": latest['dt'].strftime("%Y-%m-%d %H:%M:%S"),
            "open": float(latest['open']),
            "high": float(latest['high']),
            "low": float(latest['low']),
            "close": float(latest['close']),
            "volume": float(latest['volume']),
            "company_name": info.get('longName', ''),
            "sector": info.get('sector', ''),
            "market_cap": info.get('marketCap', ''),
            "currency": info.get('currency', 'USD'),
            "exchange": info.get('exchange', ''),
            "fetch_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        logger.info(f"Successfully fetched real-time data for {symbol}")
        return result
        
    except Exception as e:
        logger.error(f"Error fetching real-time data for {symbol}: {e}")
        return {}

def fetch_multiple_symbols(symbols: List[str], period: str = "1d", interval: str = "1h") -> Dict[str, pd.DataFrame]:
    """
    Fetch data for multiple symbols concurrently.
    """
    results = {}
    for symbol in symbols:
        try:
            df = fetch_historical_ohlcv(symbol, period=period, interval=interval)
            if not df.empty:
                results[symbol] = df
            else:
                logger.warning(f"No data for {symbol}")
        except Exception as e:
            logger.error(f"Error fetching {symbol}: {e}")
    
    return results

def get_symbol_info(symbol: str) -> Dict[str, Any]:
    """
    Get basic information about a symbol.
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        return {
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
    except Exception as e:
        logger.error(f"Error fetching symbol info for {symbol}: {e}")
        return {}
