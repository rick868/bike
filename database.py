from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey, JSON, Text, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import text
import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Get database URL from environment 
DATABASE_URL = os.getenv("DATABASE_URL")  # MySQL URL

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    inspector = inspect(engine)
    if not inspector.has_table('users'):
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    else:
        logger.info("Users table already exists, skipping creation.")

sql_statements = [
    """
    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        username VARCHAR(255) UNIQUE NOT NULL,
        hashed_password VARCHAR(255) NOT NULL
    );
    """,
    """
    CREATE INDEX ix_users_id ON users(id);
    """,
    """
    CREATE UNIQUE INDEX ix_users_username ON users(username);
    """,
    """
    CREATE TABLE motorcycles (
        id INTEGER PRIMARY KEY,
        brand VARCHAR(255),
        model_type VARCHAR(255),
        year INTEGER,
        price FLOAT,
        stock INTEGER,
        specifications JSON,
        market_position TEXT,
        competitor_prices JSON
    );
    """,
    """
    CREATE INDEX ix_motorcycles_id ON motorcycles(id);
    """,
    """
    CREATE TABLE customers (
        id INTEGER PRIMARY KEY,
        first_name VARCHAR(255),
        last_name VARCHAR(255),
        email VARCHAR(255),
        phone VARCHAR(255),
        lifetime_value FLOAT,
        purchases INTEGER,
        satisfaction_score FLOAT
    );
    """,
    """
    CREATE INDEX ix_customers_id ON customers(id);
    """,
    """
    CREATE TABLE sales (
        id INTEGER PRIMARY KEY,
        date DATE,
        motorcycle_id INTEGER,
        customer_id INTEGER,
        sales_amount FLOAT,
        units_sold INTEGER,
        customer_satisfaction FLOAT,
        sales_channel VARCHAR(255),
        promotion_applied VARCHAR(255),
        sales_region VARCHAR(255),
        FOREIGN KEY (motorcycle_id) REFERENCES motorcycles(id),
        FOREIGN KEY (customer_id) REFERENCES customers(id)
    );
    """,
    """
    CREATE INDEX ix_sales_id ON sales(id);
    """,
    """
    CREATE TABLE market_data (
        id INTEGER PRIMARY KEY,
        date DATE,
        market_share FLOAT,
        competitor_data JSON,
        economic_indicator1 JSON,  
        economic_indicator2 JSON, 
        seasonal_factors JSON,
        trend_indicators JSON
    );
    """,
    """
    CREATE INDEX ix_market_data_id ON market_data(id);
    """
]

if __name__ == "__main__":
    init_db()
    print("Database initialized.")

class Motorcycle(Base):
    __tablename__ = "motorcycles"

    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String(255))
    model_type = Column(String(255))
    price = Column(Float)
    year = Column(Integer)
    stock = Column(Integer)
    specifications = Column(JSON)  # Store detailed specs
    market_position = Column(Text)  # Market positioning data
    competitor_prices = Column(JSON)  # Competitor pricing data

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    motorcycle_id = Column(Integer, ForeignKey('motorcycles.id'))
    customer_id = Column(Integer, ForeignKey('customers.id'))
    sales_amount = Column(Float)
    units_sold = Column(Integer)
    customer_satisfaction = Column(Float)
    sales_channel = Column(String(255))  # Online/Offline/Dealer
    promotion_applied = Column(String(255))  # Type of promotion if any
    sales_region = Column(String(255))

    motorcycle = relationship("Motorcycle")
    customer = relationship("Customer")

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(255))  # Add firstname field
    last_name = Column(String(255))  # Add lastname field
    email = Column(String(255))  # Add email field
    phone = Column(String(255))  # Add phone field
    lifetime_value = Column(Float, default=0.0)
    purchases = Column(Integer, default=0)
    satisfaction_score = Column(Float, default=0.0)

class MarketData(Base):
    __tablename__ = "market_data"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    region = Column(String(255))
    market_size = Column(Float)
    market_share = Column(Float)
    competitor_data = Column(JSON)
    economic_indicators = Column(JSON)  # GDP, disposable income, etc.
    seasonal_factors = Column(JSON)
    trend_indicators = Column(JSON)
