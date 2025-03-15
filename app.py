import streamlit as st
import pandas as pd
from data_generator import generate_motorcycle_data, generate_sales_data, generate_customer_data
from models import MotorcycleDSS
from utils import create_sales_trend_chart, create_inventory_pie_chart, create_customer_satisfaction_gauge, export_to_csv

# Initialize session state
if 'inventory_data' not in st.session_state:
    st.session_state.inventory_data = generate_motorcycle_data()
if 'sales_data' not in st.session_state:
    st.session_state.sales_data = generate_sales_data()
if 'customer_data' not in st.session_state:
    st.session_state.customer_data = generate_customer_data()

# Initialize DSS model
dss = MotorcycleDSS(
    st.session_state.inventory_data,
    st.session_state.sales_data,
    st.session_state.customer_data
)

st.title("Motorcycle Dealership DSS")

# Sidebar for navigation
page = st.sidebar.selectbox(
    "Select Dashboard",
    ["Overview", "Inventory Management", "Sales Analytics", "Customer Insights", "Forecasting"]
)

if page == "Overview":
    st.header("Dashboard Overview")
    
    # Key metrics in columns
    col1, col2, col3 = st.columns(3)
    
    inventory_metrics = dss.get_inventory_metrics()
    sales_metrics = dss.get_sales_metrics()
    customer_metrics = dss.get_customer_metrics()
    
    with col1:
        st.metric("Total Inventory", f"{inventory_metrics['total_inventory']:,}")
        st.metric("Average Price", f"${inventory_metrics['avg_price']:,.2f}")
    
    with col2:
        st.metric("Total Sales", f"${sales_metrics['total_sales']:,.2f}")
        st.metric("Units Sold", f"{sales_metrics['total_units']:,}")
    
    with col3:
        st.metric("Total Customers", f"{customer_metrics['total_customers']:,}")
        st.metric("Avg. Customer LTV", f"${customer_metrics['avg_ltv']:,.2f}")
    
    # Charts
    st.plotly_chart(create_sales_trend_chart(st.session_state.sales_data))
    st.plotly_chart(create_inventory_pie_chart(st.session_state.inventory_data))

elif page == "Inventory Management":
    st.header("Inventory Management")
    
    # Add new inventory
    with st.expander("Add New Inventory"):
        col1, col2 = st.columns(2)
        with col1:
            brand = st.selectbox("Brand", ['Honda', 'Yamaha', 'Kawasaki', 'Suzuki', 'Ducati', 'BMW', 'KTM'])
            model_type = st.selectbox("Model Type", ['Sport', 'Cruiser', 'Adventure', 'Touring', 'Naked'])
        with col2:
            price = st.number_input("Price", min_value=1000.0, max_value=50000.0, value=10000.0)
            stock = st.number_input("Stock", min_value=0, max_value=100, value=1)
        
        if st.button("Add Inventory"):
            new_row = pd.DataFrame({
                'id': [st.session_state.inventory_data['id'].max() + 1],
                'brand': [brand],
                'model_type': [model_type],
                'price': [price],
                'year': [2023],
                'stock': [stock]
            })
            st.session_state.inventory_data = pd.concat([st.session_state.inventory_data, new_row], ignore_index=True)
            st.success("Inventory added successfully!")
    
    # Display inventory table
    st.dataframe(st.session_state.inventory_data)
    
    # Export inventory
    csv = export_to_csv(st.session_state.inventory_data, "inventory.csv")
    st.download_button(
        label="Download Inventory Data",
        data=csv,
        file_name="inventory.csv",
        mime="text/csv"
    )

elif page == "Sales Analytics":
    st.header("Sales Analytics")
    
    sales_metrics = dss.get_sales_metrics()
    st.metric("Total Sales", f"${sales_metrics['total_sales']:,.2f}")
    st.metric("Average Customer Satisfaction", f"{sales_metrics['avg_satisfaction']:.1f}/5.0")
    
    st.plotly_chart(create_sales_trend_chart(st.session_state.sales_data))
    
    # Monthly sales breakdown
    monthly_sales = st.session_state.sales_data.set_index('date').resample('M')['sales_amount'].sum()
    st.line_chart(monthly_sales)

elif page == "Customer Insights":
    st.header("Customer Insights")
    
    customer_metrics = dss.get_customer_metrics()
    st.metric("Average Customer Lifetime Value", f"${customer_metrics['avg_ltv']:,.2f}")
    st.metric("Average Purchases per Customer", f"{customer_metrics['avg_purchases']:.1f}")
    
    st.plotly_chart(create_customer_satisfaction_gauge(st.session_state.customer_data))
    
    # Customer distribution
    st.dataframe(st.session_state.customer_data)

elif page == "Forecasting":
    st.header("Sales Forecasting")
    
    forecast_days = st.slider("Forecast Days", 7, 90, 30)
    forecast = dss.forecast_sales(periods=forecast_days)
    
    st.line_chart(forecast)
    
    st.write("Forecast Summary:")
    st.metric("Forecasted Average Daily Sales", f"${forecast.mean():,.2f}")
    st.metric("Forecasted Total Sales", f"${forecast.sum():,.2f}")
