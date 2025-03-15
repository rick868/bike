import pandas as pd
import numpy as np
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from prophet import Prophet
from datetime import datetime, timedelta
import json

class DataAnalytics:
    def __init__(self, db_session):
        self.db = db_session
        
    def import_csv_data(self, file_path, table_name):
        """Import data from CSV file into specified table"""
        df = pd.read_csv(file_path)
        if table_name == 'motorcycles':
            df.to_sql('motorcycles', self.db.bind, if_exists='append', index=False)
        elif table_name == 'customers':
            df.to_sql('customers', self.db.bind, if_exists='append', index=False)
        elif table_name == 'sales':
            df.to_sql('sales', self.db.bind, if_exists='append', index=False)
        elif table_name == 'market_data':
            df.to_sql('market_data', self.db.bind, if_exists='append', index=False)
    
    def statistical_analysis(self, data_type):
        """Perform statistical analysis on different data types"""
        if data_type == 'sales':
            sales_df = pd.read_sql('SELECT * FROM sales', self.db.bind)
            analysis = {
                'total_revenue': sales_df['sales_amount'].sum(),
                'avg_transaction': sales_df['sales_amount'].mean(),
                'sales_growth': self._calculate_growth_rate(sales_df, 'sales_amount'),
                'seasonal_patterns': self._analyze_seasonality(sales_df),
                'top_regions': sales_df.groupby('sales_region')['sales_amount'].sum().nlargest(5).to_dict()
            }
            return analysis
            
    def customer_segmentation(self):
        """Perform customer segmentation using K-means clustering"""
        customer_df = pd.read_sql('SELECT * FROM customers', self.db.bind)
        features = ['lifetime_value', 'purchases', 'satisfaction_score']
        
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(customer_df[features])
        
        kmeans = KMeans(n_clusters=4, random_state=42)
        customer_df['segment'] = kmeans.fit_predict(scaled_features)
        
        segments = {
            'high_value': customer_df[customer_df['segment'] == 0].shape[0],
            'medium_value': customer_df[customer_df['segment'] == 1].shape[0],
            'low_value': customer_df[customer_df['segment'] == 2].shape[0],
            'at_risk': customer_df[customer_df['segment'] == 3].shape[0]
        }
        return segments
        
    def sales_forecast(self, periods=30):
        """Generate sales forecast using Prophet"""
        sales_df = pd.read_sql('SELECT date, sales_amount FROM sales', self.db.bind)
        sales_df.columns = ['ds', 'y']
        
        model = Prophet(yearly_seasonality=True, weekly_seasonality=True)
        model.fit(sales_df)
        
        future_dates = model.make_future_dataframe(periods=periods)
        forecast = model.predict(future_dates)
        
        return {
            'dates': forecast['ds'].tail(periods).tolist(),
            'predictions': forecast['yhat'].tail(periods).tolist(),
            'lower_bound': forecast['yhat_lower'].tail(periods).tolist(),
            'upper_bound': forecast['yhat_upper'].tail(periods).tolist()
        }
        
    def what_if_analysis(self, scenario):
        """Perform what-if analysis based on different scenarios"""
        base_sales = pd.read_sql('SELECT * FROM sales', self.db.bind)
        
        if scenario == 'price_increase':
            impact = {
                'revenue_change': base_sales['sales_amount'].sum() * 1.1,
                'demand_change': base_sales['units_sold'].sum() * 0.9,
                'profit_margin': 'Increased by 5%'
            }
        elif scenario == 'marketing_boost':
            impact = {
                'revenue_change': base_sales['sales_amount'].sum() * 1.15,
                'customer_acquisition': 'Increased by 20%',
                'roi': '12% on marketing spend'
            }
        return impact
        
    def _calculate_growth_rate(self, df, column):
        """Calculate year-over-year growth rate"""
        current = df[column].sum()
        previous = df[df['date'] <= datetime.now() - timedelta(days=365)][column].sum()
        return (current - previous) / previous * 100 if previous else 0
        
    def _analyze_seasonality(self, df):
        """Analyze seasonal patterns in data"""
        monthly_sales = df.set_index('date').resample('M')['sales_amount'].sum()
        return monthly_sales.to_dict()

class CRMAnalytics:
    def __init__(self, db_session):
        self.db = db_session
        
    def customer_lifetime_value(self):
        """Calculate and analyze customer lifetime value"""
        customer_df = pd.read_sql('SELECT * FROM customers', self.db.bind)
        clv_analysis = {
            'average_clv': customer_df['lifetime_value'].mean(),
            'median_clv': customer_df['lifetime_value'].median(),
            'top_customers': customer_df.nlargest(10, 'lifetime_value')[['name', 'lifetime_value']].to_dict()
        }
        return clv_analysis
        
    def churn_risk_analysis(self):
        """Identify customers at risk of churning"""
        customers = pd.read_sql('''
            SELECT c.*, COUNT(s.id) as recent_purchases
            FROM customers c
            LEFT JOIN sales s ON c.id = s.customer_id
            AND s.date >= NOW() - INTERVAL '6 months'
            GROUP BY c.id
        ''', self.db.bind)
        
        customers['churn_risk'] = np.where(
            (customers['recent_purchases'] == 0) & 
            (customers['satisfaction_score'] < 3.5),
            'High',
            np.where(
                customers['satisfaction_score'] < 4.0,
                'Medium',
                'Low'
            )
        )
        
        return customers.groupby('churn_risk').size().to_dict()
