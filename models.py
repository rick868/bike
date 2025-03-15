from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from database import Motorcycle, Sale, Customer

class MotorcycleDSS:
    def __init__(self, db: Session):
        self.db = db

    def get_inventory_metrics(self):
        total_inventory = self.db.query(func.sum(Motorcycle.stock)).scalar() or 0
        avg_price = self.db.query(func.avg(Motorcycle.price)).scalar() or 0
        low_stock_items = self.db.query(Motorcycle).filter(Motorcycle.stock < 5).count()

        return {
            'total_inventory': total_inventory,
            'avg_price': float(avg_price),
            'low_stock_items': low_stock_items
        }

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