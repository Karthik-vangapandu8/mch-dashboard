import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Telangana Transport Registration Analysis",
    page_icon="🚗",
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

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('ts_transport_registration_01_11_2024to30_11_2024.csv')
    df['fromdate'] = pd.to_datetime(df['fromdate'], format='%d/%m/%Y')
    df['todate'] = pd.to_datetime(df['todate'], format='%d/%m/%Y')
    return df

try:
    # Load the data
    df = load_data()
    
    # Title and description
    st.title("🚗 Telangana Transport Registration Analysis")
    st.markdown("""
    Comprehensive analysis of vehicle registrations in Telangana with real-time filtering and interactive visualizations.
    """)

    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Date range filter
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(df['fromdate'].min(), df['fromdate'].max()),
        min_value=df['fromdate'].min(),
        max_value=df['fromdate'].max()
    )
    
    # RTA Office filter
    offices = ['All'] + sorted(df['OfficeCd'].unique().tolist())
    selected_offices = st.sidebar.multiselect(
        "Select RTA Offices",
        options=offices[1:],
        default=[]
    )
    
    # Vehicle type filter
    vehicle_types = ['All'] + sorted(df['bodyType'].unique().tolist())
    selected_vehicle_type = st.sidebar.selectbox(
        "Select Vehicle Type",
        options=vehicle_types
    )
    
    # Apply filters
    mask = (df['fromdate'].dt.date >= date_range[0]) & (df['fromdate'].dt.date <= date_range[1])
    filtered_df = df[mask]
    
    if selected_offices:
        filtered_df = filtered_df[filtered_df['OfficeCd'].isin(selected_offices)]
    
    if selected_vehicle_type != 'All':
        filtered_df = filtered_df[filtered_df['bodyType'] == selected_vehicle_type]
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>Total Registrations</h3>
            <h2>{:,}</h2>
        </div>
        """.format(len(filtered_df)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>Active RTA Offices</h3>
            <h2>{}</h2>
        </div>
        """.format(filtered_df['OfficeCd'].nunique()), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>Vehicle Types</h3>
            <h2>{}</h2>
        </div>
        """.format(filtered_df['bodyType'].nunique()), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>Unique Manufacturers</h3>
            <h2>{}</h2>
        </div>
        """.format(filtered_df['makerName'].nunique()), unsafe_allow_html=True)
    
    # Create tabs for different analyses
    tab1, tab2, tab3, tab4 = st.tabs([
        "Registration Trends",
        "Vehicle Analysis",
        "Manufacturer Insights",
        "Geographic Distribution"
    ])
    
    with tab1:
        st.header("Registration Trends")
        
        # Daily Registration Trend
        daily_reg = filtered_df.groupby('fromdate').size().reset_index(name='count')
        fig_trend = px.line(
            daily_reg,
            x='fromdate',
            y='count',
            title='Daily Registration Trend'
        )
        fig_trend.update_traces(line_color='#1f77b4')
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # Registration by Day of Week
        filtered_df['day_of_week'] = filtered_df['fromdate'].dt.day_name()
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow_reg = filtered_df.groupby('day_of_week').size().reindex(day_order).reset_index(name='count')
        
        fig_dow = px.bar(
            dow_reg,
            x='day_of_week',
            y='count',
            title='Registrations by Day of Week'
        )
        st.plotly_chart(fig_dow, use_container_width=True)
    
    with tab2:
        st.header("Vehicle Analysis")
        
        # Vehicle Type Distribution
        vehicle_dist = filtered_df.groupby('bodyType').size().reset_index(name='count')
        fig_vehicle = px.pie(
            vehicle_dist,
            values='count',
            names='bodyType',
            title='Vehicle Type Distribution',
            hole=0.4
        )
        st.plotly_chart(fig_vehicle, use_container_width=True)
        
        # Fuel Type Analysis
        fuel_dist = filtered_df.groupby('fuel').size().reset_index(name='count')
        fig_fuel = px.bar(
            fuel_dist.sort_values('count', ascending=True),
            x='count',
            y='fuel',
            orientation='h',
            title='Distribution by Fuel Type'
        )
        st.plotly_chart(fig_fuel, use_container_width=True)
    
    with tab3:
        st.header("Manufacturer Insights")
        
        # Top Manufacturers
        manufacturer_dist = filtered_df.groupby('makerName').size().reset_index(name='count')
        fig_manufacturer = px.bar(
            manufacturer_dist.sort_values('count', ascending=False).head(15),
            x='makerName',
            y='count',
            title='Top 15 Manufacturers'
        )
        fig_manufacturer.update_xaxes(tickangle=45)
        st.plotly_chart(fig_manufacturer, use_container_width=True)
        
        # Popular Models
        model_dist = filtered_df.groupby('modelDesc').size().reset_index(name='count')
        fig_models = px.bar(
            model_dist.sort_values('count', ascending=False).head(10),
            x='count',
            y='modelDesc',
            orientation='h',
            title='Top 10 Vehicle Models'
        )
        st.plotly_chart(fig_models, use_container_width=True)
    
    with tab4:
        st.header("Geographic Distribution")
        
        # RTA Office Performance
        office_perf = filtered_df.groupby('OfficeCd').size().reset_index(name='count')
        fig_office = px.bar(
            office_perf.sort_values('count', ascending=True).tail(15),
            x='count',
            y='OfficeCd',
            orientation='h',
            title='Top RTA Offices by Registration Volume'
        )
        st.plotly_chart(fig_office, use_container_width=True)
        
        # Daily Performance by Office
        if len(selected_offices) > 0:
            office_daily = filtered_df[filtered_df['OfficeCd'].isin(selected_offices)].groupby(
                ['fromdate', 'OfficeCd']
            ).size().reset_index(name='count')
            
            fig_office_trend = px.line(
                office_daily,
                x='fromdate',
                y='count',
                color='OfficeCd',
                title='Daily Registration Trend by Selected RTA Offices'
            )
            st.plotly_chart(fig_office_trend, use_container_width=True)

except Exception as e:
    st.error(f"Error loading or processing the data: {str(e)}")
    st.markdown("""
    Please ensure:
    1. The file 'ts_transport_registration_01_11_2024to30_11_2024.csv' is in the same directory
    2. The CSV file contains all required columns
    3. The date format in the CSV matches '%d/%m/%Y'
    """)
