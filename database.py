from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL')

# Create database engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
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
    name = Column(String)
    email = Column(String, unique=True)
    phone = Column(String)
    address = Column(String)
    lifetime_value = Column(Float)
    purchases = Column(Integer)
    satisfaction_score = Column(Float)
    preferences = Column(JSON)  # Store customer preferences
    interaction_history = Column(JSON)  # Store interaction timeline
    segment = Column(String)  # Customer segment category

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
    Base.metadata.create_all(bind=engine)

# Get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()