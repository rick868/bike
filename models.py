from sqlalchemy.orm import Session
from sqlalchemy import JSON, Text, create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from database import Motorcycle, Sale, Customer

Base = declarative_base()

class User(Base):  # Define User model
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)  # Store hashed password

class Motorcycle(Base):
    __tablename__ = 'motorcycles'
    id = Column(Integer, primary_key=True, index=True)
    brand = Column(String)
    model_type = Column(String)
    year = Column(Integer)
    price = Column(Float)
    stock = Column(Integer)
    specifications = Column(JSON)  # Store detailed specs
    market_position = Column(Text)  # Market positioning data
    competitor_prices = Column(JSON)  # Competitor pricing data

class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String) # Assuming you've corrected this column name
    email = Column(String)
    phone = Column(String)
    lifetime_value = Column(Float)
    purchases = Column(Integer)
    satisfaction_score = Column(Float)

class Sales(Base):
    __tablename__ = 'sales'
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    motorcycle_id = Column(Integer, ForeignKey('motorcycles.id'))
    customer_id = Column(Integer, ForeignKey('customers.id'))
    sales_amount = Column(Float)
    units_sold = Column(Integer)
    customer_satisfaction = Column(Float)  # Customer satisfaction score
    sales_channel = Column(String)  # Online/Offline/Dealer
    promotion_applied = Column(String)  # Type of promotion if any
    sales_region = Column(String)  # Sales region
    motorcycle = relationship("Motorcycle")
    customer = relationship("Customer")

class MarketData(Base):
    __tablename__ = 'market_data'
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    market_share = Column(Float)
    competitor_data = Column(JSON)
    economic_indicators = Column(JSON)  # GDP, disposable income, etc.
    seasonal_factors = Column(JSON)
    trend_indicators = Column(JSON)

class MotorcycleDSS:
    def __init__(self, db: Session):
        self.db = db

    def get_inventory_metrics(self):
        try:
            print("Fetching inventory metrics...") # Debug print
            total_inventory = self.db.query(Motorcycle).count()
            avg_price = self.db.query(func.avg(Motorcycle.price)).scalar()
            print("Inventory metrics fetched successfully.") # Debug print
            return {
                'total_inventory': total_inventory,
                'avg_price': avg_price if avg_price else 0  # Handle potential None
            }
        except Exception as e:
            print(f"Error fetching inventory metrics: {e}") # Error print
            raise # Re-raise the exception to be caught in app.py
    
    def get_sales_metrics(self):
        total_sales = self.db.query(func.sum(Sale.sales_amount)).scalar() or 0
        avg_satisfaction = self.db.query(func.avg(Sale.customer_satisfaction)).scalar() or 0
        total_units = self.db.query(func.sum(Sale.units_sold)).scalar() or 0

        return {
            'total_sales': float(total_sales),
            'avg_satisfaction': float(avg_satisfaction),
            'total_units': total_units
        }

    def get_customer_metrics(self):
        avg_ltv = self.db.query(func.avg(Customer.lifetime_value)).scalar() or 0
        total_customers = self.db.query(Customer).count()
        avg_purchases = self.db.query(func.avg(Customer.purchases)).scalar() or 0

        return {
            'avg_ltv': float(avg_ltv),
            'total_customers': total_customers,
            'avg_purchases': float(avg_purchases)
        }

    def get_sales_data(self):
        sales = self.db.query(Sale).all()
        return pd.DataFrame([{
            'date': sale.date,
            'sales_amount': sale.sales_amount,
            'units_sold': sale.units_sold,
            'customer_satisfaction': sale.customer_satisfaction
        } for sale in sales])

    def get_inventory_data(self):
        inventory = self.db.query(Motorcycle).all()
        return pd.DataFrame([{
            'id': moto.id,
            'brand': moto.brand,
            'model_type': moto.model_type,
            'price': moto.price,
            'year': moto.year,
            'stock': moto.stock
        } for moto in inventory])

    def get_customer_data(self):
        customers = self.db.query(Customer).all()
        return pd.DataFrame([{
            'customer_id': cust.id,
            'lifetime_value': cust.lifetime_value,
            'purchases': cust.purchases,
            'satisfaction_score': cust.satisfaction_score
        } for cust in customers])

    def forecast_sales(self, periods=30):
        daily_sales = self.get_sales_data()
        daily_sales = daily_sales.set_index('date')['sales_amount'].resample('D').mean()
        forecast = daily_sales.rolling(window=7).mean().iloc[-1] * np.random.uniform(0.9, 1.1, periods)
        dates = pd.date_range(start=datetime.now(), periods=periods, freq='D')
        return pd.Series(forecast, index=dates)
