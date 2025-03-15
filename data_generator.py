import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_motorcycle_data(n_records=100):
    brands = ['Honda', 'Yamaha', 'Kawasaki', 'Suzuki', 'Ducati', 'BMW', 'KTM']
    models = ['Sport', 'Cruiser', 'Adventure', 'Touring', 'Naked']
    
    np.random.seed(42)
    
    data = {
        'id': range(1, n_records + 1),
        'brand': np.random.choice(brands, n_records),
        'model_type': np.random.choice(models, n_records),
        'price': np.random.uniform(5000, 25000, n_records).round(2),
        'year': np.random.randint(2018, 2024, n_records),
        'stock': np.random.randint(0, 20, n_records)
    }
    
    return pd.DataFrame(data)

def generate_sales_data(n_records=500):
    dates = pd.date_range(
        start=datetime.now() - timedelta(days=365),
        end=datetime.now(),
        periods=n_records
    )
    
    data = {
        'date': dates,
        'sales_amount': np.random.uniform(5000, 30000, n_records).round(2),
        'units_sold': np.random.randint(1, 5, n_records),
        'customer_satisfaction': np.random.uniform(3.5, 5.0, n_records).round(1)
    }
    
    return pd.DataFrame(data)

def generate_customer_data(n_records=200):
    data = {
        'customer_id': range(1, n_records + 1),
        'lifetime_value': np.random.uniform(5000, 100000, n_records).round(2),
        'purchases': np.random.randint(1, 5, n_records),
        'satisfaction_score': np.random.uniform(3.0, 5.0, n_records).round(1)
    }
    
    return pd.DataFrame(data)
