# models.py
from sqlalchemy import Column, Integer, Float, String, DateTime, PrimaryKeyConstraint
from db import Base

class OHLCV(Base):
    __tablename__ = "ohlcv"
    
    # Composite primary key: symbol + datetime
    __table_args__ = (
        PrimaryKeyConstraint('symbol', 'dt'),
    )
    
    symbol = Column(String(32), nullable=False, index=True)
    dt = Column(DateTime, nullable=False, index=True)
    open = Column(Float, nullable=True)
    high = Column(Float, nullable=True)
    low = Column(Float, nullable=True)
    close = Column(Float, nullable=True)
    volume = Column(Float, nullable=True)
    source = Column(String(64), nullable=True, default='yfinance')
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
