import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Custom color palette
COLORS = {
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'accent1': '#2ca02c',
    'accent2': '#d62728',
    'background': '#f0f8ff',
    'metric_bg': 'linear-gradient(135deg, #a8e6cf 0%, #dcedc1 100%)',
    'text': '#1e1e1e'
}

# Set page config
st.set_page_config(
    page_title="EV Hatchback Analysis Dashboard",
    page_icon="🚗",
    layout="wide"
)

# Custom CSS with enhanced colors
st.markdown("""
    <style>
    .main {
        background-color: #f0f8ff;
    }
    .metric-card {
        background: linear-gradient(135deg, #a8e6cf 0%, #dcedc1 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .metric-card h3 {
        color: #2c3e50;
        font-size: 1.1em;
        margin-bottom: 10px;
    }
    .metric-card h2 {
        color: #1e1e1e;
        font-size: 2em;
        font-weight: bold;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background: linear-gradient(135deg, #ffd3b6 0%, #ffaaa5 100%);
        border-radius: 10px;
        padding: 10px 20px;
        font-size: 16px;
        font-weight: 500;
        color: #2c3e50;
        transition: all 0.3s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: linear-gradient(135deg, #ffaaa5 0%, #ff8b94 100%);
        transform: translateY(-2px);
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, #a8e6cf 0%, #3eacff 100%);
        color: white;
    }
    .stMarkdown {
        color: #2c3e50;
    }
    .st-emotion-cache-1y4p8pa {
        max-width: 100%;
    }
    div[data-testid="stSidebarNav"] {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 10px;
    }
    .dashboard-title {
        background: linear-gradient(120deg, #FF6B6B, #4ECDC4, #45B7D1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 48px;
        font-weight: 800;
        text-align: center;
        padding: 20px;
        margin-bottom: 30px;
        text-transform: uppercase;
        letter-spacing: 2px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        animation: titleGlow 3s ease-in-out infinite;
    }
    @keyframes titleGlow {
        0% { transform: scale(1); }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    .dashboard-subtitle {
        color: #2c3e50;
        text-align: center;
        font-size: 20px;
        font-weight: 500;
        margin-bottom: 40px;
        padding: 10px;
        background: linear-gradient(to right, #f8f9fa, #e9ecef, #f8f9fa);
        border-radius: 10px;
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
    # Load and filter data
    df = load_data()
    ev_data = df[df['fuel'].str.contains('BATTERY', na=False)]
    hatchbacks = ev_data[ev_data['bodyType'] == 'HATCHBACK']
    
    # Title and description
    st.markdown('<h1 class="dashboard-title">🚗 Electric Hatchback Analysis Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="dashboard-subtitle">Comprehensive analysis of electric hatchback registrations in Telangana. Track market trends, popular models, and geographic distribution.</p>', unsafe_allow_html=True)
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Date range filter
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(hatchbacks['fromdate'].min(), hatchbacks['fromdate'].max()),
        min_value=hatchbacks['fromdate'].min(),
        max_value=hatchbacks['fromdate'].max()
    )
    
    # Manufacturer filter
    manufacturers = ['All'] + sorted(hatchbacks['makerName'].unique().tolist())
    selected_manufacturer = st.sidebar.selectbox(
        "Select Manufacturer",
        options=manufacturers
    )
    
    # Apply filters
    mask = (hatchbacks['fromdate'].dt.date >= date_range[0]) & (hatchbacks['fromdate'].dt.date <= date_range[1])
    filtered_data = hatchbacks[mask]
    
    if selected_manufacturer != 'All':
        filtered_data = filtered_data[filtered_data['makerName'] == selected_manufacturer]
    
    # Calculate market share with proper filtering
    ev_mask = (ev_data['fromdate'].dt.date >= date_range[0]) & (ev_data['fromdate'].dt.date <= date_range[1])
    filtered_ev_data = ev_data[ev_mask]
    market_share = (len(filtered_data) / len(filtered_ev_data) * 100)
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Total Hatchbacks</h3>
            <h2>{len(filtered_data):,}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>EV Market Share</h3>
            <h2>{market_share:.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Unique Models</h3>
            <h2>{filtered_data['modelDesc'].nunique()}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>Active RTA Offices</h3>
            <h2>{filtered_data['OfficeCd'].nunique()}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Create tabs for different analyses
    tab1, tab2, tab3 = st.tabs([
        "Market Overview",
        "Model Analysis",
        "Geographic Distribution"
    ])
    
    with tab1:
        st.header("Market Overview")
        
        # Daily Registration Trend
        daily_reg = filtered_data.groupby('fromdate').size().reset_index(name='count')
        fig_trend = px.line(
            daily_reg,
            x=np.array(daily_reg['fromdate'].dt.to_pydatetime()),
            y='count',
            title='Daily Hatchback Registration Trend'
        )
        fig_trend.update_traces(line_color='#3eacff', line_width=3)
        fig_trend.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            title_font=dict(size=24, color='#2c3e50'),
            showlegend=False,
            hovermode='x unified',
            hoverlabel=dict(bgcolor='white'),
            xaxis=dict(showgrid=True, gridwidth=1, gridcolor='#f0f0f0'),
            yaxis=dict(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # Manufacturer Market Share
        manufacturer_share = filtered_data.groupby('makerName').size().reset_index(name='count')
        fig_manufacturer = px.pie(
            manufacturer_share,
            values='count',
            names='makerName',
            title='Manufacturer Market Share',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_manufacturer.update_layout(
            title_font=dict(size=24, color='#2c3e50'),
            paper_bgcolor='white'
        )
        fig_manufacturer.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hoverinfo='label+percent+value',
            marker=dict(line=dict(color='white', width=2))
        )
        st.plotly_chart(fig_manufacturer, use_container_width=True)
    
    with tab2:
        st.header("Model Analysis")
        
        # Top Models
        model_dist = filtered_data.groupby('modelDesc').size().reset_index(name='count')
        fig_models = px.bar(
            model_dist.sort_values('count', ascending=False).head(10),
            x='modelDesc',
            y='count',
            title='Top 10 Hatchback Models',
            color='count',
            color_continuous_scale='Viridis'
        )
        fig_models.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            title_font=dict(size=24, color='#2c3e50'),
            showlegend=False,
            xaxis_tickangle=-45,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
        )
        st.plotly_chart(fig_models, use_container_width=True)
        
        # Technical Specifications
        if 'hp' in filtered_data.columns and 'seatCapacity' in filtered_data.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                fig_hp = px.box(
                    filtered_data,
                    x='makerName',
                    y='hp',
                    title='Horsepower Distribution by Manufacturer'
                )
                st.plotly_chart(fig_hp, use_container_width=True)
            
            with col2:
                seat_dist = filtered_data.groupby('seatCapacity').size().reset_index(name='count')
                fig_seats = px.bar(
                    seat_dist,
                    x='seatCapacity',
                    y='count',
                    title='Seating Capacity Distribution'
                )
                st.plotly_chart(fig_seats, use_container_width=True)
    
    with tab3:
        st.header("Geographic Distribution")
        
        # RTA Office Distribution
        office_dist = filtered_data.groupby('OfficeCd').agg({
            'registrationNo': 'count',
            'makerName': lambda x: ', '.join(x.value_counts().head(3).index),
            'modelDesc': lambda x: ', '.join(x.value_counts().head(3).index)
        }).reset_index()
        
        office_dist.columns = ['RTA Office', 'Number of Hatchbacks', 'Top 3 Manufacturers', 'Top 3 Models']
        office_dist['Percentage'] = (office_dist['Number of Hatchbacks'] / office_dist['Number of Hatchbacks'].sum() * 100).round(2)
        
        # Office Performance Chart
        fig_office = px.bar(
            office_dist.sort_values('Number of Hatchbacks', ascending=True).tail(15),
            x='Number of Hatchbacks',
            y='RTA Office',
            orientation='h',
            title='Top RTA Offices by Hatchback Registration',
            color='Number of Hatchbacks',
            color_continuous_scale='Viridis'
        )
        fig_office.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            title_font=dict(size=24, color='#2c3e50'),
            showlegend=False,
            xaxis=dict(showgrid=True, gridwidth=1, gridcolor='#f0f0f0'),
            yaxis=dict(showgrid=False)
        )
        st.plotly_chart(fig_office, use_container_width=True)
        
        # Detailed Office Analysis
        st.subheader("Detailed RTA Office Analysis")
        st.dataframe(
            office_dist.sort_values('Number of Hatchbacks', ascending=False),
            hide_index=True,
            column_config={
                'Number of Hatchbacks': st.column_config.NumberColumn(format="%d"),
                'Percentage': st.column_config.NumberColumn(format="%.2f%%")
            }
        )

except Exception as e:
    st.error(f"Error in analysis: {str(e)}")
    st.markdown("""
    Please ensure:
    1. The file 'ts_transport_registration_01_11_2024to30_11_2024.csv' is present
    2. The CSV file contains all required columns
    3. The date format matches '%d/%m/%Y'
    """)
