import pandas as pd
import numpy as np
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from prophet import Prophet
from datetime import datetime, timedelta
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_error, mean_squared_error
import json
import logging

logger = logging.getLogger(__name__)

class DataAnalytics:
    def __init__(self, db_session):
        self.db = db_session

    def import_csv_data(self, file_path, table_name):
        """Import data from CSV file into specified table"""
        try:
            df = pd.read_csv(file_path)
            if table_name == 'motorcycles':
                df.to_sql('motorcycles', self.db.bind, if_exists='append', index=False)
            elif table_name == 'customers':
                df.to_sql('customers', self.db.bind, if_exists='append', index=False)
            elif table_name == 'sales':
                df.to_sql('sales', self.db.bind, if_exists='append', index=False)
            elif table_name == 'market_data':
                df.to_sql('market_data', self.db.bind, if_exists='append', index=False)
            logger.info(f"Successfully imported data to {table_name}")
        except Exception as e:
            logger.error(f"Error importing data: {str(e)}")
            raise

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

    def sales_forecast(self, periods=30, model_type='prophet', params=None):
        """Generate sales forecast using multiple models"""
        try:
            sales_df = pd.read_sql(
                'SELECT date, sales_amount FROM sales ORDER BY date',
                self.db.bind
            )

            if model_type == 'prophet':
                return self._prophet_forecast(sales_df, periods, params)
            elif model_type == 'arima':
                return self._arima_forecast(sales_df, periods, params)
            elif model_type == 'ensemble':
                return self._ensemble_forecast(sales_df, periods, params)
            else:
                raise ValueError(f"Unknown model type: {model_type}")

        except Exception as e:
            logger.error(f"Forecasting error: {str(e)}")
            raise

    def _prophet_forecast(self, df, periods, params=None):
        """Prophet model forecasting"""
        df_prophet = df.rename(columns={'date': 'ds', 'sales_amount': 'y'})

        model_params = {
            'yearly_seasonality': True,
            'weekly_seasonality': True,
            'daily_seasonality': False,
            'uncertainty_samples': 1000
        }
        if params:
            model_params.update(params)

        model = Prophet(**model_params)
        model.add_country_holidays(country_name='US')
        model.fit(df_prophet)

        future_dates = model.make_future_dataframe(periods=periods)
        forecast = model.predict(future_dates)

        # Calculate performance metrics
        y_true = df_prophet['y'].values
        y_pred = forecast['yhat'][:len(y_true)]
        metrics = self._calculate_metrics(y_true, y_pred)

        return {
            'dates': forecast['ds'].tail(periods).tolist(),
            'predictions': forecast['yhat'].tail(periods).tolist(),
            'lower_bound': forecast['yhat_lower'].tail(periods).tolist(),
            'upper_bound': forecast['yhat_upper'].tail(periods).tolist(),
            'metrics': metrics
        }

    def _arima_forecast(self, df, periods, params=None):
        """ARIMA model forecasting"""
        model_params = {'order': (1, 1, 1)} if not params else params

        model = ARIMA(df['sales_amount'].values, **model_params)
        results = model.fit()

        forecast = results.forecast(steps=periods)
        conf_int = results.get_forecast(steps=periods).conf_int()

        # Calculate performance metrics
        y_true = df['sales_amount'].values
        y_pred = results.fittedvalues
        metrics = self._calculate_metrics(y_true, y_pred)

        return {
            'dates': [df['date'].max() + timedelta(days=i) for i in range(1, periods + 1)],
            'predictions': forecast.tolist(),
            'lower_bound': conf_int[:, 0].tolist(),
            'upper_bound': conf_int[:, 1].tolist(),
            'metrics': metrics
        }

    def _ensemble_forecast(self, df, periods, params=None):
        """Ensemble forecasting combining multiple models"""
        prophet_forecast = self._prophet_forecast(df, periods, params)
        arima_forecast = self._arima_forecast(df, periods, params)

        # Simple average ensemble
        predictions = np.mean([
            prophet_forecast['predictions'],
            arima_forecast['predictions']
        ], axis=0)

        lower_bound = np.mean([
            prophet_forecast['lower_bound'],
            arima_forecast['lower_bound']
        ], axis=0)

        upper_bound = np.mean([
            prophet_forecast['upper_bound'],
            arima_forecast['upper_bound']
        ], axis=0)

        return {
            'dates': prophet_forecast['dates'],
            'predictions': predictions.tolist(),
            'lower_bound': lower_bound.tolist(),
            'upper_bound': upper_bound.tolist(),
            'metrics': {
                'prophet': prophet_forecast['metrics'],
                'arima': arima_forecast['metrics']
            }
        }

    def _calculate_metrics(self, y_true, y_pred):
        """Calculate forecast performance metrics"""
        return {
            'mae': mean_absolute_error(y_true, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_true, y_pred)),
            'mape': np.mean(np.abs((y_true - y_pred) / y_true)) * 100
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
        df['date'] = pd.to_datetime(df['date'])
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

        print("Columns in customer_df:", customer_df.columns) 
        
            # Combine first and last name into a 'name' column (if these columns exist)
        if 'first_name' in customer_df.columns and 'last_name' in customer_df.columns:
            customer_df['name'] = customer_df['first_name'] + ' ' + customer_df['last_name']
        elif 'customer_name' in customer_df.columns: # Or if it's 'customer_name'
            customer_df = customer_df.rename(columns={'customer_name': 'name'}) # Rename to 'name'
        else:
            logger.warning("No valid name column found in customer_df.")
            customer_df['name'] = 'Unknown'  # Assign a default value if no names are available
            
        clv_analysis = {
            'average_clv': customer_df['lifetime_value'].mean(),
            'median_clv': customer_df['lifetime_value'].median(),
            'top_customers': customer_df.nlargest(10, 'lifetime_value')[['name', 'lifetime_value']].to_dict()
        }
        return clv_analysis

    def churn_risk_analysis(self):
        """Identify customers at risk of churning"""
        customers = pd.read_sql('''
            SELECT c.id, c.first_name, c.last_name, c.email, c.phone, c.lifetime_value, c.purchases, c.satisfaction_score, COUNT(s.id) as recent_purchases
            FROM customers c
            LEFT JOIN sales s ON c.id = s.customer_id
            GROUP BY c.id, c.first_name, c.last_name, c.email, c.phone, c.lifetime_value, c.purchases, c.satisfaction_score
        ''', self.db)
