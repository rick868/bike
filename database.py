from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
import logging

logger = logging.getLogger(__name__)

# Get database URL from environment or use SQLite as fallback
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    logger.warning("DATABASE_URL not found, using SQLite fallback")
    DATABASE_URL = 'sqlite:///dealership.db'
elif 'postgres' in DATABASE_URL:
    # Add SSL mode for PostgreSQL connections
    DATABASE_URL = f"{DATABASE_URL}?sslmode=require"

try:
    # Create database engine with PostgreSQL compatible settings
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10
    )
    logger.info("Database engine created successfully")
except Exception as e:
    logger.error(f"Failed to create database engine: {str(e)}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Motorcycle(Base):
    __tablename__ = "motorcycles"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String)
    model_type = Column(String)
    price = Column(Float)
    year = Column(Integer)
    stock = Column(Integer)

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    motorcycle_id = Column(Integer, ForeignKey('motorcycles.id'))
    customer_id = Column(Integer, ForeignKey('customers.id'))
    sales_amount = Column(Float)
    units_sold = Column(Integer)
    customer_satisfaction = Column(Float)
    sales_channel = Column(String)  # Online/Offline/Dealer
    promotion_applied = Column(String)  # Type of promotion if any
    sales_region = Column(String)

    motorcycle = relationship("Motorcycle")
    customer = relationship("Customer")

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    lifetime_value = Column(Float, default=0.0)
    purchases = Column(Integer, default=0)
    satisfaction_score = Column(Float, default=0.0)

class MarketData(Base):
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    region = Column(String)
    market_size = Column(Float)
    market_share = Column(Float)
    competitor_data = Column(JSON)
    economic_indicators = Column(JSON)  # GDP, disposable income, etc.
    seasonal_factors = Column(JSON)
    trend_indicators = Column(JSON)

# Create all tables
def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {str(e)}")
        raise

# Get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()