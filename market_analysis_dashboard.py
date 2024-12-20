import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import numpy as np

# Set page configuration
st.set_page_config(
    page_title="Agricultural Market Intelligence Dashboard",
    page_icon="🌾",
    layout="wide"
)

# Add custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stPlotlyChart {
        background-color: white;
        border-radius: 5px;
        padding: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Load and preprocess data
@st.cache_data
def load_data():
    df = pd.read_csv('day_prices_between_01-11-2024_30-11-2024.csv')
    df['DDate'] = pd.to_datetime(df['DDate'])
    return df

# Main title
st.title("🌾 Agricultural Market Intelligence Dashboard")
st.markdown("---")

# Load the data
df = load_data()

# Sidebar filters
st.sidebar.header("Filters")
selected_commodity = st.sidebar.multiselect(
    "Select Commodity",
    options=sorted(df['CommName'].unique()),
    default=['Paddy', 'Onions'] if 'Paddy' in df['CommName'].unique() else df['CommName'].unique()[:2]
)

# Filter the data
filtered_df = df[df['CommName'].isin(selected_commodity)]

# Top metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Markets", filtered_df['YardName'].nunique())
with col2:
    st.metric("Total Commodities", filtered_df['CommName'].nunique())
with col3:
    avg_price = filtered_df['Model'].mean()
    st.metric("Average Price (₹)", f"{avg_price:,.2f}")
with col4:
    total_arrivals = filtered_df['Arrivals'].sum()
    st.metric("Total Arrivals (Quintals)", f"{total_arrivals:,.2f}")

# Price Analysis
st.markdown("## 📈 Price Analysis")
col1, col2 = st.columns(2)

with col1:
    # Price Trends
    st.subheader("Price Trends Over Time")
    price_trends = filtered_df.groupby(['DDate', 'CommName'])['Model'].mean().reset_index()
    fig_trends = px.line(
        price_trends, 
        x='DDate', 
        y='Model', 
        color='CommName',
        title='Average Daily Prices'
    )
    st.plotly_chart(fig_trends, use_container_width=True)

with col2:
    # Price Distribution
    st.subheader("Price Distribution by Commodity")
    fig_dist = px.box(
        filtered_df,
        x='CommName',
        y='Model',
        title='Price Distribution'
    )
    st.plotly_chart(fig_dist, use_container_width=True)

# Market Analysis
st.markdown("## 🏪 Market Analysis")
col1, col2 = st.columns(2)

with col1:
    # Top Markets by Volume
    top_markets = filtered_df.groupby('YardName')['Arrivals'].sum().sort_values(ascending=False).head(10)
    fig_markets = px.bar(
        x=top_markets.index,
        y=top_markets.values,
        title='Top 10 Markets by Volume'
    )
    st.plotly_chart(fig_markets, use_container_width=True)

with col2:
    # Price Variation Across Markets
    market_stats = filtered_df.groupby('YardName').agg({
        'Model': ['mean', 'std']
    }).reset_index()
    market_stats.columns = ['YardName', 'Mean_Price', 'Price_Std']
    fig_variation = px.scatter(
        market_stats,
        x='Mean_Price',
        y='Price_Std',
        hover_data=['YardName'],
        title='Price Variation Across Markets'
    )
    st.plotly_chart(fig_variation, use_container_width=True)

# Opportunity Analysis
st.markdown("## 💡 Market Opportunities")

# Calculate price differences between markets
def calculate_arbitrage():
    daily_prices = filtered_df.groupby(['DDate', 'CommName', 'YardName'])['Model'].mean().reset_index()
    opportunities = []
    
    for date in daily_prices['DDate'].unique():
        for comm in daily_prices['CommName'].unique():
            day_data = daily_prices[(daily_prices['DDate'] == date) & (daily_prices['CommName'] == comm)]
            if len(day_data) > 1:
                min_price = day_data['Model'].min()
                max_price = day_data['Model'].max()
                if min_price > 0:  # Avoid division by zero
                    price_diff_pct = ((max_price - min_price) / min_price) * 100
                    if price_diff_pct > 10:  # Only show opportunities with >10% difference
                        opportunities.append({
                            'Date': date,
                            'Commodity': comm,
                            'Min_Price_Market': day_data.loc[day_data['Model'].idxmin(), 'YardName'],
                            'Max_Price_Market': day_data.loc[day_data['Model'].idxmax(), 'YardName'],
                            'Min_Price': min_price,
                            'Max_Price': max_price,
                            'Price_Difference_Pct': price_diff_pct
                        })
    
    return pd.DataFrame(opportunities)

opportunities_df = calculate_arbitrage()

if not opportunities_df.empty:
    st.markdown("### Price Arbitrage Opportunities")
    st.markdown("Markets with significant price differences (>10%) for the same commodity")
    st.dataframe(
        opportunities_df.sort_values('Price_Difference_Pct', ascending=False),
        hide_index=True
    )

# Download section
st.markdown("---")
st.markdown("### 📥 Download Analysis")

# Prepare download data
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df_to_csv(opportunities_df)
st.download_button(
    "Download Opportunities Data",
    csv,
    "market_opportunities.csv",
    "text/csv",
    key='download-csv'
)
