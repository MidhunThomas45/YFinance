# services/storage_service.py
from sqlalchemy.orm import Session
from sqlalchemy import text
from db import get_db, engine
from models import OHLCV
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def upsert_ohlcv_from_df(df: pd.DataFrame) -> int:
    """
    Upsert OHLCV data from DataFrame to database.
    Returns number of rows processed.
    """
    if df.empty:
        return 0
    
    try:
        # Convert DataFrame to list of dictionaries
        records = df.to_dict(orient='records')
        
        # Add timestamps
        current_time = datetime.now()
        for record in records:
            record['created_at'] = current_time
            record['updated_at'] = current_time
            record['source'] = 'yfinance'
        
        # Use raw SQL for better performance on bulk upsert
        with engine.connect() as conn:
            # Create temporary table
            temp_table_name = f"temp_ohlcv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Insert into temporary table
            df.to_sql(temp_table_name, conn, if_exists='replace', index=False)
            
            # Upsert from temporary table to main table
            upsert_sql = f"""
                INSERT INTO ohlcv (symbol, dt, open, high, low, close, volume, source, created_at, updated_at)
                SELECT symbol, dt, open, high, low, close, volume, source, created_at, updated_at
                FROM {temp_table_name}
                ON DUPLICATE KEY UPDATE
                    open = VALUES(open),
                    high = VALUES(high),
                    low = VALUES(low),
                    close = VALUES(close),
                    volume = VALUES(volume),
                    updated_at = VALUES(updated_at)
            """
            
            result = conn.execute(text(upsert_sql))
            conn.commit()
            
            # Drop temporary table
            conn.execute(text(f"DROP TABLE {temp_table_name}"))
            
            logger.info(f"Successfully upserted {len(records)} records for {df['symbol'].iloc[0]}")
            return len(records)
            
    except Exception as e:
        logger.error(f"Error upserting data: {e}")
        return 0

def query_ohlcv(symbol: str, limit: int = 100) -> list:
    """
    Query OHLCV data from database for a specific symbol.
    """
    try:
        with engine.connect() as conn:
            query = text("""
                SELECT symbol, dt, open, high, low, close, volume, source
                FROM ohlcv 
                WHERE symbol = :symbol 
                ORDER BY dt DESC 
                LIMIT :limit
            """)
            
            result = conn.execute(query, {"symbol": symbol.upper(), "limit": limit})
            rows = result.fetchall()
            
            # Convert to list of dictionaries
            data = []
            for row in rows:
                data.append({
                    "symbol": row.symbol,
                    "dt": row.dt.strftime("%Y-%m-%d %H:%M:%S") if row.dt else None,
                    "open": float(row.open) if row.open else None,
                    "high": float(row.high) if row.high else None,
                    "low": float(row.low) if row.low else None,
                    "close": float(row.close) if row.close else None,
                    "volume": float(row.volume) if row.volume else None,
                    "source": row.source
                })
            
            return data
            
    except Exception as e:
        logger.error(f"Error querying data: {e}")
        return []

def get_symbols_from_db() -> list:
    """
    Get list of all symbols available in database.
    """
    try:
        with engine.connect() as conn:
            query = text("SELECT DISTINCT symbol FROM ohlcv ORDER BY symbol")
            result = conn.execute(query)
            symbols = [row.symbol for row in result.fetchall()]
            return symbols
    except Exception as e:
        logger.error(f"Error getting symbols: {e}")
        return []
