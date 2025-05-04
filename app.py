import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from database import get_db, init_db
from data_generator import populate_database
from models import MotorcycleDSS, Motorcycle, User
from analytics import DataAnalytics, CRMAnalytics
from utils import create_sales_trend_chart, create_inventory_pie_chart, create_customer_satisfaction_gauge, export_to_csv
import logging
import bcrypt # Import bcrypt for password hashing
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError # Import IntegrityError for handling duplicate entries

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Voyager Dealership",
    page_icon="🏍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None

# Custom CSS
st.markdown("""
    <style>
    .reportview-container {
        background: #f8f9fa;
    }
    .sidebar .sidebar-content {
        background: #ffffff;
        border-right: 1px solid #e9ecef;
    }
    .stButton>button {
        width: 100%;
        margin-bottom: 10px;
        background-color: #007bff;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 5px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #0056b3;
        transform: translateY(-2px);
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .stProgress .st-bo {
        background-color: #007bff;
    }
    .stMetric {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: transform 0.3s ease;
    }
    .stMetric:hover {
        transform: translateY(-2px);
    }
    .big-font {
        font-size: 24px !important;
        font-weight: bold;
        color: #2c3e50;
    }
    .feature-box {
        padding: 1.5rem;
        border-radius: 8px;
        background-color: white;
        margin: 15px 0;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    .feature-box:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .centered-text {
        text-align: center;
    }
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1.5rem 0;
        margin-bottom: 2rem;
        border-bottom: 1px solid #e9ecef;
    }
    .login-btn {
        background-color: #007bff;
        color: white;
        padding: 0.75rem 1.5rem;
        border-radius: 5px;
        text-decoration: none;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .login-btn:hover {
        background-color: #0056b3;
        transform: translateY(-2px);
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .login-container {
        max-width: 400px;
        margin: 3rem auto;
        padding: 2rem;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        background: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .st-emotion-cache-16txtl3 h1 {
        font-weight: 600;
        color: #2c3e50;
    }
    .st-emotion-cache-16txtl3 h2, .st-emotion-cache-16txtl3 h3 {
        color: #34495e;
        margin-top: 2rem;
    }
    .st-emotion-cache-16txtl3 p {
        color: #596275;
        line-height: 1.6;
    }
    </style>
""", unsafe_allow_html=True)

# --- Authentication Functions ---

def get_user_by_username(db: Session, username: str):
    try:
        return db.query(User).filter(User.username == username).first()
    except Exception as e:
        logger.error(f"Error retrieving user by username: {str(e)}")
        return None


def create_user(db: Session, username: str, password: str, role: str = 'user'):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    db_user = User(username=username, hashed_password=hashed_password,)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def login(db: Session, username, password):
    user = get_user_by_username(db, username)
    if user and verify_password(password, user.hashed_password):
        st.session_state.authenticated = True
        st.session_state.username = username
        return True
    return False

# --- Authentication Page ---
def auth_page():
    db = next(get_db())  # Initialize the database session
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        login_username = st.text_input("Username")
        login_password = st.text_input("Password", type="password")
        if st.button("Login"):
            # Use the initialized db session for login
            if login(db, login_username, login_password):
                st.success("Login successful!")

                st.session_state.show_login_page = False
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Invalid credentials")
            db.close()

    with tab2:
        signup_username = st.text_input("Username for Signup")
        signup_password = st.text_input("Password for Signup", type="password")
        signup_confirm_password = st.text_input("Confirm Password", type="password")

        if st.button("Sign Up"):
            try:
                if get_user_by_username(db, signup_username):
                    st.error("Username already taken. Please choose another.")
                else:
                    create_user(db, signup_username, signup_password,)  # Pass the role to the create_user function
                st.success("Signup successful! Please log in.")
                st.session_state.show_login_page = True
                st.session_state.show_signup_page = False
                st.rerun()
            except IntegrityError:
                st.error("Username already taken. Please choose another.")
            if signup_password != signup_confirm_password:
                st.error("Passwords do not match.")
            elif len(signup_password) < 6:
                st.error("Password must be at least 6 characters long.")
            else:
                try:
                    db = next(get_db())
                    create_user(db, signup_username, signup_password)
                    st.success("Signup successful! Please log in.")
                    st.session_state.show_login_page = True
                    st.session_state.show_signup_page = False
                    st.rerun()
                except IntegrityError:
                    st.error("Username already taken. Please choose another.")
                except Exception as e:
                    logger.error(f"Signup error: {str(e)}")
                    st.error(f"Signup failed: {str(e)}")
                finally:
                    db.close()

# Logout function
def logout():
    st.session_state.authenticated = False
    st.session_state.username = None
    st.rerun()

# Initialize session state for authentication - simplified
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'username' not in st.session_state:
    st.session_state.username = None

# Display header with logo
st.markdown("""
    <div class="header-container">
        <img src="static/voyager_logo.svg" alt="Voyager Logo" width="200">
        <div>
""" + (f"""
            <span style="margin-right: 1rem; color: #6c757d;">Welcome, {st.session_state.username}</span>
            """ +  """
            <button class="login-btn" onclick="window.location.href='/logout';">Logout</button>
            """ + """
""" if st.session_state.authenticated else """
            <button class="login-btn" onclick="window.location.href='/login';">Login</button>
""") + """
        </div>
    </div>
""", unsafe_allow_html=True)

# Initialize session state for dss if it doesn't exist
if 'dss' not in st.session_state:
    st.session_state.dss = MotorcycleDSS(next(get_db()))  # Initialize with the actual DSS class

# Main application logic - Conditionally render auth page or main app
if not st.session_state.authenticated:
    auth_page() # Show authentication page if not logged in
else:
    def display_header():
        st.markdown("<h1 class='centered-text'>Welcome to Voyager</h1>", unsafe_allow_html=True)
        st.markdown("<h2 class='centered-text'>Motorcycle Dealership Intelligence Platform</h2>", unsafe_allow_html=True)

    display_header() # Display header after successful login

    # Main application content (authenticated users)

    # Initialize database and models (only once authenticated)
    if 'db_initialized' not in st.session_state: # Check if initialized already
        try:
            logger.info("Initializing database...")
            logger.error("Failed to initialize database. Please check the logs.")
            init_db()
            logger.info("Populating database with sample data...")
            populate_database()

            # Create default admin user if not exists (for initial setup)
            db = next(get_db())
            if not get_user_by_username(db, "admin"):
                create_user(db, "admin", "admin") # Default admin/admin credentials
                logger.info("Default admin user created.")
            db.close()

            st.session_state.db_initialized = True # Mark as initialized
            logger.info("Database initialization complete")
        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}")
            st.error("Failed to initialize database. Please check the logs.")
            st.stop()

    try:
        if 'dss_initialized' not in st.session_state: # Check if DSS models initialized
            logger.info("Creating database session...")
            db = next(get_db())
            logger.info("Database session created successfully")
            logger.info("Initializing DSS models...")
            st.session_state.dss = MotorcycleDSS(db) # Store in session state
            st.session_state.data_analytics = DataAnalytics(db) # Store in session state
            st.session_state.crm_analytics = CRMAnalytics(db) # Store in session state
            st.session_state.db_session = db # Store db session for later use if needed
            st.session_state.dss_initialized = True # Mark DSS models as initialized
            logger.info("Models initialized successfully")
        else:
            db = st.session_state.db_session # Reuse existing session
            dss = st.session_state.dss
            data_analytics = st.session_state.data_analytics
            crm_analytics = st.session_state.crm_analytics

    except Exception as e:
        logger.error(f"Failed to initialize models: {str(e)}")
        st.error("Failed to initialize application models. Please check the logs.")
        st.stop()

# Sidebar navigation with icons (only shown when authenticated)
st.sidebar.title("Navigation")
page = st.sidebar.selectbox(
    "Select Page",
    ["🏠 Home", "📊 Dashboard", "📦 Inventory", "💰 Sales", 
     "👥 Customers", "📈 Market", "🔮 Forecast", 
     "🎯 What-If", "📥 Data"]
)
# User Profile Display in Sidebar
if st.session_state.authenticated:
    st.sidebar.markdown("---") # Separator
    st.sidebar.markdown(f"**User Profile**")
    st.sidebar.markdown(f"**Username:** {st.session_state.username}")
    st.sidebar.markdown("---") # Separator
    
# Main content area
if page == "🏠 Home":

    st.markdown("""
        <div class='centered-text'>
        Transform your dealership with AI-powered insights and advanced analytics
        </div>
    """, unsafe_allow_html=True)

    # Add a logout button using st.button - outside the markdown for proper Streamlit handling
    if st.session_state.authenticated: # Only show logout button if authenticated
        if st.sidebar.button("Logout"): # Place it in sidebar or anywhere outside markdown
            logout() # Call your Python logout function

    # Quick Stats
    try:
        metrics = st.session_state.dss.get_inventory_metrics()
        sales = st.session_state.dss.get_sales_metrics()
        customers = st.session_state.dss.get_customer_metrics()

        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"📦 {metrics['total_inventory']} Motorcycles in Stock")
        with col2:
            st.info(f"💰 ${sales['total_sales']:,.0f} Total Sales")
        with col3:
            st.info(f"👥 {customers['total_customers']} Active Customers")
    except Exception as e:
        logger.error(f"Error loading quick stats: {str(e)}")
        st.warning("Quick stats temporarily unavailable")

    # Feature Sections
    st.markdown("### Key Features")

    col1, col2 = st.columns(2)

    with col1:
        with st.container():
            st.markdown("""
            <div class='feature-box'>
                <h4>📊  Sales Analytics </h4>
                <ul>
                    <li>Real-time sales tracking</li>
                    <li>Performance metrics</li>
                    <li>Regional analysis</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        with st.container():
            st.markdown("""
                <div class='feature-box'>
                   <h4>🔮 Advanced Forecasting </h4>
                    <ul>
                        <li>Machine learning models</li>
                        <li>Trend analysis</li>
                        <li>Seasonal predictions</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

    with col2:
        with st.container():
            st.markdown("""
            <div class='feature-box'>
               <h4>👥 Customer Insights </h4>
                <ul>
                    <li>Customer segmentation</li>
                    <li>Lifetime value analysis</li>
                    <li>Satisfaction tracking</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        with st.container():
            st.markdown("""
                <div class='feature-box'>
                    <h4>📈 Market Intelligence</h4>
                    <ul>
                        <li>Competitive analysis</li>
                        <li>Market trends</li>
                        <li>Price optimization</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

    # Quick Access Buttons
    st.markdown("### Quick Access")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📊 View Dashboard"):
            st.session_state.page = "📊 Dashboard"
            st.rerun()
    with col2:
        if st.button("📦 Manage Inventory"):
            st.session_state.page = "📦 Inventory"
            st.rerun()
    with col3:
        if st.button("💰 Sales Analytics"):
            st.session_state.page = "💰 Sales"
            st.rerun()

elif page == "📊 Dashboard":
    st.header("Dashboard Overview")

    with st.spinner("Loading metrics..."):
        try:
            inventory_metrics = st.session_state.dss.get_inventory_metrics()
            sales_metrics = st.session_state.dss.get_sales_metrics()
            customer_metrics = st.session_state.dss.get_customer_metrics()

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
                sales_data = st.session_state.dss.get_sales_data()
                st.plotly_chart(
                    create_sales_trend_chart(sales_data),
                    use_container_width=True
                )

            with col2:
                inventory_data = st.session_state.dss.get_inventory_data()
                st.plotly_chart(
                    create_inventory_pie_chart(inventory_data),
                    use_container_width=True
                )

        except Exception as e:
            logger.error(f"Error loading overview metrics: {str(e)}")
            st.error("Failed to load metrics. Please try refreshing the page.")

elif page == "📦 Inventory":
    st.header("Inventory Management")

    # Add new inventory
    with st.expander("Add New Inventory"):
        col1, col2 = st.columns(2)
        with col1:
            brand = st.text_input("Brand", placeholder="Enter the brand of the motorcycle")
            model_type = st.text_input("Model Type", placeholder="Enter the model type of the motorcycle")
        with col2:
            price = st.number_input("Price (KSH)", min_value=50000.0, value=1000000.0)
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
    inventory_data = st.session_state.dss.get_inventory_data()
    st.dataframe(inventory_data)

    # Export inventory
    csv = export_to_csv(inventory_data, "inventory.csv")
    st.download_button(
        label="Download Inventory Data",
        data=csv,
        file_name="inventory.csv",
        mime="text/csv"
    )

elif page == "💰 Sales":
    st.header("Sales Analytics")

    # Statistical Analysis
    stats = st.session_state.data_analytics.statistical_analysis('sales')

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Revenue", f"${stats['total_revenue']:,.2f}")
        st.metric("Sales Growth", f"{stats['sales_growth']:.1f}%")

    with col2:
        st.metric("Average Transaction", f"${stats['avg_transaction']:,.2f}")

    # Sales Trends
    st.subheader("Sales Trends")
    sales_data = st.session_state.dss.get_sales_data()
    st.plotly_chart(create_sales_trend_chart(sales_data))

    # Regional Performance
    st.subheader("Top Performing Regions")
    regions_df = pd.DataFrame(list(stats['top_regions'].items()), 
                            columns=['Region', 'Sales'])
    st.bar_chart(regions_df.set_index('Region'))

elif page == "👥 Customers":
    st.header("Customer Insights")

    # Customer Segmentation
    segments = st.session_state.data_analytics.customer_segmentation()
    st.subheader("Customer Segments")

    segment_df = pd.DataFrame(list(segments.items()), 
                            columns=['Segment', 'Count'])
    st.plotly_chart(px.pie(segment_df, values='Count', names='Segment',
                          title='Customer Segmentation'))

    # Customer Lifetime Value Analysis
    clv_data = st.session_state.crm_analytics.customer_lifetime_value()
    st.metric("Average Customer Lifetime Value", 
              f"${clv_data['average_clv']:,.2f}")

    # Churn Risk Analysis
    churn_data = st.session_state.crm_analytics.churn_risk_analysis()
    st.subheader("Churn Risk Distribution")
    churn_df = pd.DataFrame(list(churn_data.items()),
                           columns=['Risk Level', 'Count'])
    st.bar_chart(churn_df.set_index('Risk Level'))

elif page == "📈 Market":
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

elif page == "🔮 Forecast":
    st.header("Sales Forecasting")

    # Model selection and parameters
    col1, col2 = st.columns(2)
    with col1:
        model_type = st.selectbox(
            "Select Forecasting Model",
            ["prophet", "arima", "ensemble"],
            help="Choose the forecasting model to use"
        )
        periods = st.slider(
            "Forecast Periods (Days)", 
            7, 90, 30,
            help="Number of days to forecast into the future"
        )

    with col2:
        if model_type == "prophet":
            yearly_seasonality = st.checkbox("Include Yearly Seasonality", value=True)
            weekly_seasonality = st.checkbox("Include Weekly Seasonality", value=True)
            params = {
                'yearly_seasonality': yearly_seasonality,
                'weekly_seasonality': weekly_seasonality
            }
        elif model_type == "arima":
            p = st.number_input("AR Order (p)", 0, 5, 1)
            d = st.number_input("Difference Order (d)", 0, 2, 1)
            q = st.number_input("MA Order (q)", 0, 5, 1)
            params = {'order': (p, d, q)}
        else:
            params = None

    # Generate forecast
    with st.spinner("Generating forecast..."):
        try:
            forecast = st.session_state.data_analytics.sales_forecast(
                periods=periods,
                model_type=model_type,
                params=params
            )

            # Create forecast visualization
            forecast_df = pd.DataFrame({
                'Date': forecast['dates'],
                'Forecast': forecast['predictions'],
                'Lower Bound': forecast['lower_bound'],
                'Upper Bound': forecast['upper_bound']
            })

            # Plot the forecast
            st.subheader("Sales Forecast")
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=forecast_df['Date'],
                y=forecast_df['Forecast'],
                name='Forecast',
                line=dict(color='#007bff')
            ))
            fig.add_trace(go.Scatter(
                x=forecast_df['Date'],
                y=forecast_df['Upper Bound'],
                fill=None,
                mode='lines',
                line=dict(color='rgba(0,123,255,0.2)'),
                name='Upper Bound'
            ))
            fig.add_trace(go.Scatter(
                x=forecast_df['Date'],
                y=forecast_df['Lower Bound'],
                fill='tonexty',
                mode='lines',
                line=dict(color='rgba(0,123,255,0.2)'),
                name='Lower Bound'
            ))
            fig.update_layout(
                title='Sales Forecast with Confidence Intervals',
                xaxis_title='Date',
                yaxis_title='Sales Amount ($)',
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)

            # Display metrics
            st.subheader("Forecast Metrics")
            metrics = forecast['metrics']
            if isinstance(metrics, dict):
                if model_type == 'ensemble':
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("Prophet Model Metrics")
                        for k, v in metrics['prophet'].items():
                            st.metric(k.upper(), f"{v:.2f}")
                    with col2:
                        st.write("ARIMA Model Metrics")
                        for k, v in metrics['arima'].items():
                            st.metric(k.upper(), f"{v:.2f}")
                else:
                    for k, v in metrics.items():
                        st.metric(k.upper(), f"{v:.2f}")

            # Summary statistics
            st.subheader("Forecast Summary")
            st.metric(
                "Average Forecasted Daily Sales",
                f"${np.mean(forecast['predictions']):,.2f}",
                help="Average daily sales predicted for the forecast period"
            )
            st.metric(
                "Total Forecasted Sales",
                f"${np.sum(forecast['predictions']):,.2f}",
                help="Total sales predicted for the entire forecast period"
            )

        except Exception as e:
            st.error(f"Error generating forecast: {str(e)}")
            logger.error(f"Forecasting error: {str(e)}")

elif page == "🎯 What-If":
    st.header("What-If Analysis")

    scenario = st.selectbox(
        "Select Scenario",
        ["price_increase", "marketing_boost"]
    )

    impact = st.session_state.data_analytics.what_if_analysis(scenario)

    st.subheader("Scenario Impact Analysis")
    for metric, value in impact.items():
        st.metric(metric.replace('_', ' ').title(), value)

elif page == "📥 Data":
    st.header("Data Import/Export")

    # File Upload
    uploaded_file = st.file_uploader("Upload CSV File", type="csv")
    if uploaded_file is not None:
        table_name = st.selectbox(
            "Select Table to Import To",
            ["motorcycles", "customers", "sales", "market_data"]
        )

        if st.button("Import Data"):
            st.session_state.data_analytics.import_csv_data(uploaded_file, table_name)
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
