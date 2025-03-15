import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from database import init_db, SessionLocal, Motorcycle, Sale, Customer

def populate_database():
    db = SessionLocal()

    # Check if data already exists
    if db.query(Motorcycle).count() > 0:
        db.close()
        return

    # Generate motorcycle data
    brands = ['Honda', 'Yamaha', 'Kawasaki', 'Suzuki', 'Ducati', 'BMW', 'KTM']
    models = ['Sport', 'Cruiser', 'Adventure', 'Touring', 'Naked']

    for _ in range(100):
        motorcycle = Motorcycle(
            brand=np.random.choice(brands),
            model_type=np.random.choice(models),
            price=round(np.random.uniform(5000, 25000), 2),
            year=np.random.randint(2018, 2024),
            stock=np.random.randint(0, 20)
        )
        db.add(motorcycle)

    # Generate sales data
    dates = pd.date_range(
        start=datetime.now() - timedelta(days=365),
        end=datetime.now(),
        periods=500
    )

    for date in dates:
        sale = Sale(
            date=date,
            sales_amount=round(np.random.uniform(5000, 30000), 2),
            units_sold=np.random.randint(1, 5),
            customer_satisfaction=round(np.random.uniform(3.5, 5.0), 1)
        )
        db.add(sale)

    # Generate customer data
    for _ in range(200):
        customer = Customer(
            lifetime_value=round(np.random.uniform(5000, 100000), 2),
            purchases=np.random.randint(1, 5),
            satisfaction_score=round(np.random.uniform(3.0, 5.0), 1)
        )
        db.add(customer)

    db.commit()
    db.close()

if __name__ == "__main__":
    init_db()
    populate_database()