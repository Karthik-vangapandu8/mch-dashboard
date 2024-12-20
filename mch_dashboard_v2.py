import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

# Set page configuration
st.set_page_config(
    page_title="MCH Kit Analysis Dashboard",
    page_icon="👶",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stPlotlyChart {
        background-color: #ffffff;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    </style>
    """, unsafe_allow_html=True)

# Load the data
@st.cache_data
def load_data():
    data = pd.read_csv('deepu.csv')
    return data

# Main title with styling
st.title('🏥 Mother and Child Health Kit Analysis Dashboard')
st.markdown('---')

try:
    data = load_data()
    
    # Dashboard Layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader('📊 Key Metrics Overview')
        total_districts = data['districtName'].nunique()
        total_mandals = data['mandalName'].nunique()
        total_villages = data['villageName'].nunique()
        total_registrations = data['pwRegCnt'].sum()
        
        metrics_col1, metrics_col2 = st.columns(2)
        with metrics_col1:
            st.metric("Total Districts", f"{total_districts:,}")
            st.metric("Total Mandals", f"{total_mandals:,}")
        with metrics_col2:
            st.metric("Total Villages", f"{total_villages:,}")
            st.metric("Total Registrations", f"{int(total_registrations):,}")
    
    with col2:
        st.subheader('📈 Registration Trends by District')
        district_reg = data.groupby('districtName')['pwRegCnt'].sum().sort_values(ascending=True)
        fig = px.bar(district_reg, orientation='h',
                    title='Pregnant Women Registrations by District',
                    labels={'value': 'Number of Registrations', 'districtName': 'District'})
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)

    # Advanced Analytics Section
    st.markdown('---')
    st.header('🔍 Advanced Analytics')
    
    # ANC Coverage Analysis
    anc_cols = ['anc1Cnt', 'anc2Cnt', 'anc3Cnt', 'anc4Cnt']
    anc_data = data[anc_cols].sum()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=['1st Visit', '2nd Visit', '3rd Visit', '4th Visit'],
        y=anc_data.values,
        text=anc_data.values,
        textposition='auto',
    ))
    fig.update_layout(
        title='ANC Visit Progression Analysis',
        xaxis_title='ANC Visits',
        yaxis_title='Number of Women',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

    # Geographical Distribution
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader('📍 Mandal-wise Kit Distribution')
        mandal_kits = data.groupby('mandalName')['kitsCnt'].sum().sort_values(ascending=False)
        fig = px.pie(values=mandal_kits.values, names=mandal_kits.index,
                    title='Kit Distribution by Mandal')
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    with col4:
        st.subheader('🎯 Delivery Statistics')
        delivery_stats = data.groupby('districtName')['delCnt'].sum().sort_values(ascending=True)
        fig = px.bar(delivery_stats,
                    title='Delivery Counts by District',
                    labels={'value': 'Number of Deliveries', 'districtName': 'District'})
        st.plotly_chart(fig, use_container_width=True)

    # Correlation Analysis
    st.markdown('---')
    st.subheader('📊 Statistical Correlations')
    
    numeric_cols = ['pwRegCnt', 'delCnt', 'kitsCnt'] + anc_cols
    corr_matrix = data[numeric_cols].corr()
    
    fig = px.imshow(corr_matrix,
                    labels=dict(color="Correlation Coefficient"),
                    x=corr_matrix.columns,
                    y=corr_matrix.columns,
                    color_continuous_scale='RdBu')
    fig.update_layout(title='Correlation Matrix of Key Metrics')
    st.plotly_chart(fig, use_container_width=True)

    # Interactive Data Explorer
    st.markdown('---')
    st.header('🔍 Interactive Data Explorer')
    
    selected_district = st.selectbox('Select District', ['All'] + list(data['districtName'].unique()))
    
    if selected_district != 'All':
        filtered_data = data[data['districtName'] == selected_district]
    else:
        filtered_data = data
    
    metric_choice = st.selectbox('Select Metric to Visualize', 
                               ['Registration Count', 'Delivery Count', 'Kit Distribution'])
    
    metric_map = {
        'Registration Count': 'pwRegCnt',
        'Delivery Count': 'delCnt',
        'Kit Distribution': 'kitsCnt'
    }
    
    selected_metric = metric_map[metric_choice]
    
    fig = px.bar(filtered_data.groupby('mandalName')[selected_metric].sum().reset_index(),
                 x='mandalName', y=selected_metric,
                 title=f'{metric_choice} by Mandal' + (f' in {selected_district}' if selected_district != 'All' else ''))
    st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"An error occurred while loading or processing the data: {str(e)}")
    st.info("Please make sure the 'deepu.csv' file is in the correct location and contains the expected columns.")

# code by Karthik-vangapandu