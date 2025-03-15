import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

def create_sales_trend_chart(sales_df):
    fig = px.line(
        sales_df,
        x='date',
        y='sales_amount',
        title='Sales Trend Over Time'
    )
    return fig

def create_inventory_pie_chart(inventory_df):
    brand_distribution = inventory_df['brand'].value_counts()
    fig = px.pie(
        values=brand_distribution.values,
        names=brand_distribution.index,
        title='Inventory Distribution by Brand'
    )
    return fig

def create_customer_satisfaction_gauge(customer_df):
    avg_satisfaction = customer_df['satisfaction_score'].mean()
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=avg_satisfaction,
        title={'text': "Average Customer Satisfaction"},
        gauge={'axis': {'range': [0, 5]},
               'steps': [
                   {'range': [0, 2], 'color': "red"},
                   {'range': [2, 3.5], 'color': "yellow"},
                   {'range': [3.5, 5], 'color': "green"}
               ],
               'threshold': {
                   'line': {'color': "black", 'width': 4},
                   'thickness': 0.75,
                   'value': avg_satisfaction
               }}
    ))
    return fig

def export_to_csv(df, filename):
    return df.to_csv(index=False).encode('utf-8')
