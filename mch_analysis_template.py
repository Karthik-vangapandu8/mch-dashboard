import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

# Set page configuration
st.set_page_config(page_title="MCH Data Analysis", layout="wide")

# Load and prepare data
@st.cache_data
def load_data():
    df = pd.read_csv('deepu.csv')
    return df

def calculate_basic_stats(df):
    """Calculate basic statistics for numerical columns"""
    return df.describe()

def analyze_anc_dropout(df):
    """Analyze dropout rates between ANC visits"""
    anc_cols = ['anc1Cnt', 'anc2Cnt', 'anc3Cnt', 'anc4Cnt']
    anc_totals = df[anc_cols].sum()
    dropout_rates = []
    
    for i in range(len(anc_cols)-1):
        dropout = (anc_totals[anc_cols[i]] - anc_totals[anc_cols[i+1]]) / anc_totals[anc_cols[i]] * 100
        dropout_rates.append(dropout)
    
    return dropout_rates

def create_geographic_analysis(df):
    """Analyze geographic distribution of healthcare metrics"""
    district_stats = df.groupby('districtName').agg({
        'pwRegCnt': 'sum',
        'delCnt': 'sum',
        'kitsCnt': 'sum',
        'highRiskCnt': 'sum'
    }).reset_index()
    return district_stats

def risk_analysis(df):
    """Analyze high-risk cases and correlations"""
    risk_correlations = df[[
        'highRiskCnt', 'pwRegCnt', 'delCnt', 
        'anc1Cnt', 'anc2Cnt', 'anc3Cnt', 'anc4Cnt'
    ]].corr()['highRiskCnt']
    return risk_correlations

def main():
    st.title("Mother and Child Health Kit Data Analysis")
    
    try:
        # Load data
        df = load_data()
        
        # Sidebar filters
        st.sidebar.header("Filters")
        selected_district = st.sidebar.selectbox(
            "Select District",
            ["All"] + list(df['districtName'].unique())
        )
        
        # Filter data based on selection
        if selected_district != "All":
            df_filtered = df[df['districtName'] == selected_district]
        else:
            df_filtered = df
            
        # Basic Statistics
        st.header("Basic Statistics")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Registrations", int(df_filtered['pwRegCnt'].sum()))
            st.metric("Total Deliveries", int(df_filtered['delCnt'].sum()))
            
        with col2:
            st.metric("High Risk Cases", int(df_filtered['highRiskCnt'].sum()))
            st.metric("Kits Distributed", int(df_filtered['kitsCnt'].sum()))
            
        # ANC Analysis
        st.header("ANC Visit Analysis")
        dropout_rates = analyze_anc_dropout(df_filtered)
        fig_anc = go.Figure()
        fig_anc.add_trace(go.Bar(
            x=['ANC1-2', 'ANC2-3', 'ANC3-4'],
            y=dropout_rates,
            text=[f"{rate:.1f}%" for rate in dropout_rates],
            textposition='auto',
        ))
        fig_anc.update_layout(title="ANC Visit Dropout Rates")
        st.plotly_chart(fig_anc)
        
        # Geographic Analysis
        st.header("Geographic Distribution")
        geo_stats = create_geographic_analysis(df_filtered)
        fig_geo = px.bar(geo_stats, 
                        x='districtName', 
                        y=['pwRegCnt', 'delCnt', 'kitsCnt'],
                        title="Healthcare Metrics by District")
        st.plotly_chart(fig_geo)
        
        # Risk Analysis
        st.header("Risk Factor Analysis")
        risk_corr = risk_analysis(df_filtered)
        fig_risk = px.bar(
            x=risk_corr.index,
            y=risk_corr.values,
            title="Correlation with High Risk Cases"
        )
        st.plotly_chart(fig_risk)
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.info("Please check your data file and try again.")

if __name__ == "__main__":
    main()
