from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum, JSON
from sqlalchemy.orm import relationship
from ..main import Base

import enum

class TradeType(enum.Enum):
    BUY = "buy"
    SELL = "sell"

class OrderStatus(enum.Enum):
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    type = Column(Enum(TradeType))
    symbol = Column(String)
    quantity = Column(Float)
    price = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    portfolio = relationship("Portfolio", back_populates="orders")

class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, unique=True, index=True)
    name = Column(String)
    current_price = Column(Float)
    last_updated = Column(DateTime, default=datetime.utcnow)

    positions = relationship("Position", back_populates="stock")
    trades = relationship("Trade", back_populates="stock")

class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"))
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    quantity = Column(Float)
    entry_price = Column(Float)
    current_value = Column(Float)

    stock = relationship("Stock", back_populates="positions")
    portfolio = relationship("Portfolio", back_populates="positions")

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"))
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"))
    quantity = Column(Float)
    price = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    type = Column(Enum(TradeType))

    stock = relationship("Stock", back_populates="trades")
    portfolio = relationship("Portfolio", back_populates="trades")

class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.user_id"))
    total_value = Column(Float, default=0.0)
    cash_balance = Column(Float, default=0.0)
    settings = Column(JSON, default={})

    positions = relationship("Position", back_populates="portfolio")
    trades = relationship("Trade", back_populates="portfolio")
    projects = relationship("Project", back_populates="portfolio")
    orders = relationship("Order", back_populates="portfolio")
