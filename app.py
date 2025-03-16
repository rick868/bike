import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from database import get_db, init_db
from data_generator import populate_database
from models import MotorcycleDSS
from analytics import DataAnalytics, CRMAnalytics
from utils import create_sales_trend_chart, create_inventory_pie_chart, create_customer_satisfaction_gauge, export_to_csv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Motorcycle Dealership DSS",
    page_icon="🏍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .reportview-container {
        background: #f8f9fa
    }
    .sidebar .sidebar-content {
        background: #ffffff
    }
    .stButton>button {
        width: 100%;
    }
    .stProgress .st-bo {
        background-color: #007bff;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize database with error handling
try:
    logger.info("Initializing database...")
    init_db()
    logger.info("Populating database with sample data...")
    populate_database()
    logger.info("Database initialization complete")
except Exception as e:
    logger.error(f"Database initialization failed: {str(e)}")
    st.error("Failed to initialize database. Please check the logs.")
    st.stop()

# Create database session with error handling
try:
    logger.info("Creating database session...")
    db = next(get_db())
    logger.info("Database session created successfully")
except Exception as e:
    logger.error(f"Failed to create database session: {str(e)}")
    st.error("Failed to connect to database. Please try again.")
    st.stop()

# Initialize models with error handling
try:
    logger.info("Initializing DSS models...")
    dss = MotorcycleDSS(db)
    data_analytics = DataAnalytics(db)
    crm_analytics = CRMAnalytics(db)
    logger.info("Models initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize models: {str(e)}")
    st.error("Failed to initialize application models. Please check the logs.")
    st.stop()

# Header
st.title("🏍️ Motorcycle Dealership DSS")
st.markdown("""
    This Decision Support System helps manage inventory, analyze sales, 
    and make data-driven decisions for your motorcycle dealership.
""")

# Sidebar navigation with icons
st.sidebar.title("Navigation")
page = st.sidebar.selectbox(
    "Select Dashboard",
    ["📊 Overview", "📦 Inventory Management", "💰 Sales Analytics", 
     "👥 Customer Insights", "📈 Market Analysis", "🔮 Forecasting", 
     "🎯 What-If Analysis", "📥 Data Import/Export"]
)

# Main content area
if page == "📊 Overview":
    st.header("Dashboard Overview")

    with st.spinner("Loading metrics..."):
        try:
            inventory_metrics = dss.get_inventory_metrics()
            sales_metrics = dss.get_sales_metrics()
            customer_metrics = dss.get_customer_metrics()

            # KPI Cards using columns
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Total Inventory",
                    f"{inventory_metrics['total_inventory']:,}",
                    help="Total number of motorcycles in stock"
                )
                st.metric(
                    "Average Price",
                    f"${inventory_metrics['avg_price']:,.2f}",
                    help="Average price of motorcycles in inventory"
                )

            with col2:
                st.metric(
                    "Total Sales",
                    f"${sales_metrics['total_sales']:,.2f}",
                    help="Total revenue from sales"
                )
                st.metric(
                    "Units Sold",
                    f"{sales_metrics['total_units']:,}",
                    help="Total number of motorcycles sold"
                )

            with col3:
                st.metric(
                    "Total Customers",
                    f"{customer_metrics['total_customers']:,}",
                    help="Total number of unique customers"
                )
                st.metric(
                    "Avg. Customer LTV",
                    f"${customer_metrics['avg_ltv']:,.2f}",
                    help="Average customer lifetime value"
                )

            # Charts
            col1, col2 = st.columns(2)
            with col1:
                sales_data = dss.get_sales_data()
                st.plotly_chart(
                    create_sales_trend_chart(sales_data),
                    use_container_width=True
                )

            with col2:
                inventory_data = dss.get_inventory_data()
                st.plotly_chart(
                    create_inventory_pie_chart(inventory_data),
                    use_container_width=True
                )

        except Exception as e:
            logger.error(f"Error loading overview metrics: {str(e)}")
            st.error("Failed to load metrics. Please try refreshing the page.")

elif page == "📦 Inventory Management":
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
            new_motorcycle = Motorcycle(
                brand=brand,
                model_type=model_type,
                price=price,
                year=2024,
                stock=stock
            )
            db.add(new_motorcycle)
            db.commit()
            st.success("Inventory added successfully!")

    # Display inventory table
    inventory_data = dss.get_inventory_data()
    st.dataframe(inventory_data)

    # Export inventory
    csv = export_to_csv(inventory_data, "inventory.csv")
    st.download_button(
        label="Download Inventory Data",
        data=csv,
        file_name="inventory.csv",
        mime="text/csv"
    )

elif page == "💰 Sales Analytics":
    st.header("Sales Analytics")

    # Statistical Analysis
    stats = data_analytics.statistical_analysis('sales')

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Revenue", f"${stats['total_revenue']:,.2f}")
        st.metric("Sales Growth", f"{stats['sales_growth']:.1f}%")

    with col2:
        st.metric("Average Transaction", f"${stats['avg_transaction']:,.2f}")

    # Sales Trends
    st.subheader("Sales Trends")
    sales_data = dss.get_sales_data()
    st.plotly_chart(create_sales_trend_chart(sales_data))

    # Regional Performance
    st.subheader("Top Performing Regions")
    regions_df = pd.DataFrame(list(stats['top_regions'].items()), 
                            columns=['Region', 'Sales'])
    st.bar_chart(regions_df.set_index('Region'))

elif page == "👥 Customer Insights":
    st.header("Customer Insights")

    # Customer Segmentation
    segments = data_analytics.customer_segmentation()
    st.subheader("Customer Segments")

    segment_df = pd.DataFrame(list(segments.items()), 
                            columns=['Segment', 'Count'])
    st.plotly_chart(px.pie(segment_df, values='Count', names='Segment',
                          title='Customer Segmentation'))

    # Customer Lifetime Value Analysis
    clv_data = crm_analytics.customer_lifetime_value()
    st.metric("Average Customer Lifetime Value", 
              f"${clv_data['average_clv']:,.2f}")

    # Churn Risk Analysis
    churn_data = crm_analytics.churn_risk_analysis()
    st.subheader("Churn Risk Distribution")
    churn_df = pd.DataFrame(list(churn_data.items()),
                           columns=['Risk Level', 'Count'])
    st.bar_chart(churn_df.set_index('Risk Level'))

elif page == "📈 Market Analysis":
    st.header("Market Analysis")

    market_data = pd.read_sql('SELECT * FROM market_data', db.bind)

    # Market Share Trend
    st.subheader("Market Share Trend")
    fig_market = px.line(market_data, x='date', y='market_share',
                        title='Market Share Over Time')
    st.plotly_chart(fig_market)

    # Economic Indicators
    st.subheader("Economic Indicators Impact")
    # Add visualization for economic indicators

elif page == "🔮 Forecasting":
    st.header("Sales Forecasting")

    periods = st.slider("Forecast Periods (Days)", 7, 90, 30)
    forecast = data_analytics.sales_forecast(periods=periods)

    # Create forecast visualization
    forecast_df = pd.DataFrame({
        'Date': forecast['dates'],
        'Forecast': forecast['predictions'],
        'Lower Bound': forecast['lower_bound'],
        'Upper Bound': forecast['upper_bound']
    })

    st.line_chart(forecast_df.set_index('Date'))

    st.write("Forecast Summary:")
    st.metric("Average Forecasted Daily Sales", 
              f"${np.mean(forecast['predictions']):,.2f}")

elif page == "🎯 What-If Analysis":
    st.header("What-If Analysis")

    scenario = st.selectbox(
        "Select Scenario",
        ["price_increase", "marketing_boost"]
    )

    impact = data_analytics.what_if_analysis(scenario)

    st.subheader("Scenario Impact Analysis")
    for metric, value in impact.items():
        st.metric(metric.replace('_', ' ').title(), value)

elif page == "📥 Data Import/Export":
    st.header("Data Import/Export")

    # File Upload
    uploaded_file = st.file_uploader("Upload CSV File", type="csv")
    if uploaded_file is not None:
        table_name = st.selectbox(
            "Select Table to Import To",
            ["motorcycles", "customers", "sales", "market_data"]
        )

        if st.button("Import Data"):
            data_analytics.import_csv_data(uploaded_file, table_name)
            st.success(f"Data imported successfully to {table_name} table!")

    # Data Export
    st.subheader("Export Data")
    export_table = st.selectbox(
        "Select Table to Export",
        ["motorcycles", "customers", "sales", "market_data"]
    )

    if st.button("Export to CSV"):
        table_data = pd.read_sql(f'SELECT * FROM {export_table}', db.bind)
        csv = export_to_csv(table_data, f"{export_table}.csv")
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"{export_table}.csv",
            mime="text/csv"
        )