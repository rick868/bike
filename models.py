import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class MotorcycleDSS:
    def __init__(self, inventory_df, sales_df, customer_df):
        self.inventory_df = inventory_df
        self.sales_df = sales_df
        self.customer_df = customer_df

    def get_inventory_metrics(self):
        total_inventory = self.inventory_df['stock'].sum()
        avg_price = self.inventory_df['price'].mean()
        low_stock_items = len(self.inventory_df[self.inventory_df['stock'] < 5])
        
        return {
            'total_inventory': total_inventory,
            'avg_price': avg_price,
            'low_stock_items': low_stock_items
        }

    def get_sales_metrics(self):
        total_sales = self.sales_df['sales_amount'].sum()
        avg_satisfaction = self.sales_df['customer_satisfaction'].mean()
        total_units = self.sales_df['units_sold'].sum()
        
        return {
            'total_sales': total_sales,
            'avg_satisfaction': avg_satisfaction,
            'total_units': total_units
        }

    def get_customer_metrics(self):
        avg_ltv = self.customer_df['lifetime_value'].mean()
        total_customers = len(self.customer_df)
        avg_purchases = self.customer_df['purchases'].mean()
        
        return {
            'avg_ltv': avg_ltv,
            'total_customers': total_customers,
            'avg_purchases': avg_purchases
        }

    def forecast_sales(self, periods=30):
        daily_sales = self.sales_df.set_index('date')['sales_amount'].resample('D').mean()
        forecast = daily_sales.rolling(window=7).mean().iloc[-1] * np.random.uniform(0.9, 1.1, periods)
        dates = pd.date_range(start=datetime.now(), periods=periods, freq='D')
        
        return pd.Series(forecast, index=dates)
