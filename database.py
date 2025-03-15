from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
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
    sales_amount = Column(Float)
    units_sold = Column(Integer)
    customer_satisfaction = Column(Float)

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    lifetime_value = Column(Float)
    purchases = Column(Integer)
    satisfaction_score = Column(Float)

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
