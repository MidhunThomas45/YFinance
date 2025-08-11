import os
from typing import Optional

class Settings:
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql://root:password@localhost:3306/stock_data")
    
    # API settings
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # Yahoo Finance settings
    YF_TIMEOUT: int = int(os.getenv("YF_TIMEOUT", "30"))
    YF_RETRIES: int = int(os.getenv("YF_RETRIES", "3"))
    
    # Default ticker symbols
    DEFAULT_TICKERS: list = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "NFLX"
    ]

settings = Settings()
