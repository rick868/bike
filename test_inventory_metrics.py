from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import MotorcycleDSS
import os

# Set up the database connection
DATABASE_URL = "mysql+pymysql://root:Access+23#@localhost:3306/voyager_db"

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def test_inventory_metrics():
    session = Session()
    motorcycle_dss = MotorcycleDSS(session)
    metrics = motorcycle_dss.get_inventory_metrics()
    print(metrics)

if __name__ == "__main__":
    test_inventory_metrics()
