import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Set page config
st.set_page_config(
    page_title="EV Market Analysis Dashboard",
    page_icon="⚡",
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
    </style>
""", unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('ts_transport_registration_01_11_2024to30_11_2024.csv')
    df['fromdate'] = pd.to_datetime(df['fromdate'], format='%d/%m/%Y')
    return df

try:
    # Load the data
    df = load_data()
    
    # Filter for electric vehicles
    ev_data = df[df['fuel'].str.contains('BATTERY', na=False)]
    
    # Title and description
    st.title("⚡ Electric Vehicle Market Analysis Dashboard")
    st.markdown("""
    Comprehensive analysis of Electric Vehicle registrations and market trends in Telangana.
    """)
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Date range filter
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(ev_data['fromdate'].min(), ev_data['fromdate'].max()),
        min_value=ev_data['fromdate'].min(),
        max_value=ev_data['fromdate'].max()
    )
    
    # Manufacturer filter
    manufacturers = ['All'] + sorted(ev_data['makerName'].unique().tolist())
    selected_manufacturer = st.sidebar.selectbox("Select Manufacturer", manufacturers)
    
    # Apply filters
    mask = (ev_data['fromdate'].dt.date >= date_range[0]) & (ev_data['fromdate'].dt.date <= date_range[1])
    filtered_ev = ev_data[mask]
    
    if selected_manufacturer != 'All':
        filtered_ev = filtered_ev[filtered_ev['makerName'] == selected_manufacturer]
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>Total EV Registrations</h3>
            <h2>{}</h2>
        </div>
        """.format(len(filtered_ev)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>Market Share</h3>
            <h2>{:.2f}%</h2>
        </div>
        """.format((len(filtered_ev)/len(df[mask])*100)), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>Unique Models</h3>
            <h2>{}</h2>
        </div>
        """.format(filtered_ev['modelDesc'].nunique()), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>Active RTA Offices</h3>
            <h2>{}</h2>
        </div>
        """.format(filtered_ev['OfficeCd'].nunique()), unsafe_allow_html=True)
    
    # Create tabs for different analyses
    tab1, tab2, tab3 = st.tabs(["Market Share", "Geographic Distribution", "Model Analysis"])
    
    with tab1:
        st.header("Market Share Analysis")
        
        # Manufacturer Market Share
        fig_manufacturer = px.pie(
            filtered_ev,
            names='makerName',
            title='EV Manufacturer Market Share',
            hole=0.4
        )
        st.plotly_chart(fig_manufacturer, use_container_width=True)
        
        # Daily Registration Trend
        daily_reg = filtered_ev.groupby('fromdate').size().reset_index(name='count')
        fig_trend = px.line(
            daily_reg,
            x='fromdate',
            y='count',
            title='Daily EV Registration Trend'
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    
    with tab2:
        st.header("Geographic Distribution")
        
        # RTA Office Distribution
        office_ev = filtered_ev.groupby('OfficeCd').size().reset_index(name='count')
        fig_office = px.bar(
            office_ev.sort_values('count', ascending=True).tail(15),
            x='count',
            y='OfficeCd',
            orientation='h',
            title='Top RTA Offices by EV Registration'
        )
        st.plotly_chart(fig_office, use_container_width=True)
    
    with tab3:
        st.header("Model Analysis")
        
        # Top Models
        model_dist = filtered_ev.groupby('modelDesc').size().reset_index(name='count')
        fig_models = px.bar(
            model_dist.sort_values('count', ascending=False).head(10),
            x='modelDesc',
            y='count',
            title='Top 10 EV Models'
        )
        st.plotly_chart(fig_models, use_container_width=True)
        
        # Model Price Distribution
        if 'price' in filtered_ev.columns:
            fig_price = px.box(
                filtered_ev,
                x='makerName',
                y='price',
                title='EV Price Distribution by Manufacturer'
            )
            st.plotly_chart(fig_price, use_container_width=True)

except Exception as e:
    st.error(f"Error loading or processing the data: {str(e)}")
    st.markdown("""
    Please ensure:
    1. The file 'ts_transport_registration_01_11_2024to30_11_2024.csv' is in the same directory
    2. The CSV file contains the required columns
    3. The date format in the CSV matches '%d/%m/%Y'
    """)
