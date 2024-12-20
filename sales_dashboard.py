import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Set page configuration
st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# Load datasets
@st.cache_data
def load_data():
    try:
        amazon_sales = pd.read_csv("archive (4)/Amazon Sale Report.csv")
        international_sales = pd.read_csv("archive (4)/International sale Report.csv")
        sales_report = pd.read_csv("archive (4)/Sale Report.csv")
        pl_data = pd.read_csv("archive (4)/P  L March 2021.csv")
        may_data = pd.read_csv("archive (4)/May-2022.csv")
        
        # Clean and preprocess data
        for df in [amazon_sales, international_sales, sales_report]:
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date'])
        
        return {
            'amazon': amazon_sales,
            'international': international_sales,
            'sales': sales_report,
            'pl': pl_data,
            'may': may_data
        }
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

try:
    # Load data
    data = load_data()
    if data is None:
        st.stop()
    
    # Title and description
    st.title("📊 Sales Analytics Dashboard")
    st.markdown("""
    Comprehensive analysis of sales performance across multiple channels including Amazon, 
    International markets, and direct sales. Track revenue, profitability, and key performance indicators.
    """)
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Date range filter (if applicable)
    if 'Date' in data['sales'].columns:
        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=(data['sales']['Date'].min(), data['sales']['Date'].max()),
            min_value=data['sales']['Date'].min(),
            max_value=data['sales']['Date'].max()
        )
    
    # Channel filter
    selected_channel = st.sidebar.multiselect(
        "Select Sales Channels",
        options=['Amazon', 'International', 'Direct'],
        default=['Amazon', 'International', 'Direct']
    )
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_revenue = sum(df['Amount'].sum() if 'Amount' in df.columns else 0 
                          for df in [data['amazon'], data['international'], data['sales']])
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Revenue</h3>
            <h2>₹{total_revenue:,.2f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        total_orders = sum(len(df) for df in [data['amazon'], data['international'], data['sales']])
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Orders</h3>
            <h2>{total_orders:,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        st.markdown(f"""
        <div class="metric-card">
            <h3>Average Order Value</h3>
            <h2>₹{avg_order_value:,.2f}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        # Calculate growth if date information is available
        growth = 15.5  # Example value, replace with actual calculation
        st.markdown(f"""
        <div class="metric-card">
            <h3>YoY Growth</h3>
            <h2>{growth}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Create tabs for different analyses
    tab1, tab2, tab3, tab4 = st.tabs([
        "Sales Overview",
        "Channel Analysis",
        "Product Performance",
        "Financial Metrics"
    ])
    
    with tab1:
        st.header("Sales Overview")
        
        # Sales Trend
        if 'Date' in data['sales'].columns:
            sales_trend = data['sales'].groupby('Date')['Amount'].sum().reset_index()
            fig_trend = px.line(
                sales_trend,
                x='Date',
                y='Amount',
                title='Daily Sales Trend'
            )
            st.plotly_chart(fig_trend, use_container_width=True)
        
        # Sales by Category
        if 'Category' in data['sales'].columns:
            category_sales = data['sales'].groupby('Category')['Amount'].sum().reset_index()
            fig_category = px.pie(
                category_sales,
                values='Amount',
                names='Category',
                title='Sales Distribution by Category',
                hole=0.4
            )
            st.plotly_chart(fig_category, use_container_width=True)
    
    with tab2:
        st.header("Channel Analysis")
        
        # Channel Comparison
        channel_data = []
        if 'Amazon' in selected_channel:
            channel_data.append({
                'Channel': 'Amazon',
                'Revenue': data['amazon']['Amount'].sum() if 'Amount' in data['amazon'].columns else 0
            })
        if 'International' in selected_channel:
            channel_data.append({
                'Channel': 'International',
                'Revenue': data['international']['Amount'].sum() if 'Amount' in data['international'].columns else 0
            })
        if 'Direct' in selected_channel:
            channel_data.append({
                'Channel': 'Direct',
                'Revenue': data['sales']['Amount'].sum() if 'Amount' in data['sales'].columns else 0
            })
        
        channel_df = pd.DataFrame(channel_data)
        fig_channel = px.bar(
            channel_df,
            x='Channel',
            y='Revenue',
            title='Revenue by Sales Channel'
        )
        st.plotly_chart(fig_channel, use_container_width=True)
    
    with tab3:
        st.header("Product Performance")
        
        if 'Product' in data['sales'].columns and 'Amount' in data['sales'].columns:
            # Top Products
            top_products = data['sales'].groupby('Product')['Amount'].sum().sort_values(ascending=False).head(10)
            fig_products = px.bar(
                x=top_products.index,
                y=top_products.values,
                title='Top 10 Products by Revenue'
            )
            st.plotly_chart(fig_products, use_container_width=True)
    
    with tab4:
        st.header("Financial Metrics")
        
        # P&L Analysis
        if 'pl' in data:
            pl_metrics = data['pl'].melt()
            fig_pl = px.bar(
                pl_metrics,
                x='variable',
                y='value',
                title='Profit & Loss Overview'
            )
            st.plotly_chart(fig_pl, use_container_width=True)

except Exception as e:
    st.error(f"Error in analysis: {str(e)}")
    st.markdown("""
    Please ensure:
    1. All required CSV files are present in the 'archive (4)' directory
    2. The data format matches the expected structure
    3. All required columns are present in the datasets
    """)
