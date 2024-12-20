import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from scipy import stats

# Set page config
st.set_page_config(page_title="Advanced Market Patterns", layout="wide")

# Load and prepare data
@st.cache_data
def load_data():
    df = pd.read_csv('day_prices_between_01-11-2024_30-11-2024.csv')
    df['DDate'] = pd.to_datetime(df['DDate'])
    return df

df = load_data()

# Title and description
st.title("🔍 Advanced Agricultural Market Patterns")
st.markdown("""
This dashboard reveals hidden patterns and advanced insights in agricultural market data.
Use the sidebar to explore different aspects of the analysis.
""")

# Sidebar for navigation
analysis_type = st.sidebar.selectbox(
    "Select Analysis Type",
    ["Price Volatility", "Market Efficiency", "Supply Patterns", "Price Correlations", "Geographic Analysis"]
)

# 1. Price Volatility Analysis
if analysis_type == "Price Volatility":
    st.header("💹 Price Volatility Analysis")
    
    # Calculate volatility metrics
    volatility_data = df.groupby('CommName').agg({
        'Model': ['mean', 'std', 'count']
    }).reset_index()
    volatility_data.columns = ['Commodity', 'Mean_Price', 'Price_Std', 'Transaction_Count']
    volatility_data['Coefficient_of_Variation'] = (volatility_data['Price_Std'] / volatility_data['Mean_Price']) * 100
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Top volatile commodities chart
        fig_volatile = px.bar(
            volatility_data.nlargest(10, 'Coefficient_of_Variation'),
            x='Commodity',
            y='Coefficient_of_Variation',
            title='Top 10 Most Volatile Commodities',
            color='Coefficient_of_Variation',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig_volatile, use_container_width=True)
    
    with col2:
        st.metric("Most Volatile Commodity", 
                 volatility_data.iloc[0]['Commodity'],
                 f"{volatility_data.iloc[0]['Coefficient_of_Variation']:.2f}% CV")
        
        st.metric("Average Market Volatility", 
                 f"{volatility_data['Coefficient_of_Variation'].mean():.2f}%")

# 2. Market Efficiency Analysis
elif analysis_type == "Market Efficiency":
    st.header("🎯 Market Efficiency Analysis")
    
    # Calculate price spreads
    def calculate_efficiency():
        market_efficiency = []
        for comm in df['CommName'].unique():
            comm_data = df[df['CommName'] == comm]
            markets = comm_data['YardName'].unique()
            if len(markets) > 1:
                price_spreads = []
                for date in comm_data['DDate'].unique():
                    day_data = comm_data[comm_data['DDate'] == date]
                    if len(day_data) > 1:
                        price_spread = (day_data['Model'].max() - day_data['Model'].min()) / day_data['Model'].mean()
                        price_spreads.append(price_spread)
                if price_spreads:
                    market_efficiency.append({
                        'Commodity': comm,
                        'Avg_Price_Spread': np.mean(price_spreads),
                        'Market_Count': len(markets),
                        'Transaction_Count': len(comm_data)
                    })
        return pd.DataFrame(market_efficiency)
    
    efficiency_data = calculate_efficiency()
    
    # Bubble chart of market efficiency
    fig_efficiency = px.scatter(
        efficiency_data,
        x='Market_Count',
        y='Avg_Price_Spread',
        size='Transaction_Count',
        color='Avg_Price_Spread',
        hover_name='Commodity',
        title='Market Efficiency Analysis',
        labels={
            'Market_Count': 'Number of Markets',
            'Avg_Price_Spread': 'Average Price Spread',
            'Transaction_Count': 'Number of Transactions'
        }
    )
    st.plotly_chart(fig_efficiency, use_container_width=True)
    
    # Top inefficient markets
    st.subheader("Most Inefficient Markets (Highest Price Spreads)")
    st.dataframe(efficiency_data.nlargest(5, 'Avg_Price_Spread'))

# 3. Supply Patterns
elif analysis_type == "Supply Patterns":
    st.header("📦 Supply Pattern Analysis")
    
    # Calculate daily patterns
    supply_patterns = df.groupby(['DDate', 'CommName'])['Arrivals'].sum().reset_index()
    supply_patterns['DayOfWeek'] = supply_patterns['DDate'].dt.day_name()
    weekly_pattern = supply_patterns.groupby(['CommName', 'DayOfWeek'])['Arrivals'].mean().reset_index()
    
    # Select commodity
    commodity = st.selectbox("Select Commodity", sorted(df['CommName'].unique()))
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Daily supply pattern
        comm_pattern = weekly_pattern[weekly_pattern['CommName'] == commodity]
        fig_daily = px.line(
            comm_pattern,
            x='DayOfWeek',
            y='Arrivals',
            title=f'Daily Supply Pattern: {commodity}',
            markers=True
        )
        st.plotly_chart(fig_daily, use_container_width=True)
    
    with col2:
        # Supply volume distribution
        fig_dist = px.box(
            df[df['CommName'] == commodity],
            y='Arrivals',
            title=f'Supply Volume Distribution: {commodity}'
        )
        st.plotly_chart(fig_dist, use_container_width=True)

# 4. Price Correlations
elif analysis_type == "Price Correlations":
    st.header("🔗 Price Correlation Analysis")
    
    # Calculate price correlations
    daily_prices = df.groupby(['DDate', 'CommName'])['Model'].mean().reset_index()
    price_matrix = daily_prices.pivot(index='DDate', columns='CommName', values='Model')
    corr_matrix = price_matrix.corr()
    
    # Heatmap of correlations
    fig_corr = px.imshow(
        corr_matrix,
        title='Price Correlation Matrix',
        color_continuous_scale='RdBu',
        aspect='auto'
    )
    st.plotly_chart(fig_corr, use_container_width=True)
    
    # Most correlated pairs
    st.subheader("Most Correlated Commodity Pairs")
    corr_pairs = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            corr_pairs.append({
                'Commodity1': corr_matrix.columns[i],
                'Commodity2': corr_matrix.columns[j],
                'Correlation': corr_matrix.iloc[i,j]
            })
    corr_pairs_df = pd.DataFrame(corr_pairs)
    st.dataframe(corr_pairs_df.nlargest(10, 'Correlation'))

# 5. Geographic Analysis
elif analysis_type == "Geographic Analysis":
    st.header("🗺️ Geographic Market Analysis")
    
    # Calculate market metrics
    market_data = df.groupby('YardName').agg({
        'Model': ['mean', 'std'],
        'Arrivals': 'sum',
        'CommName': 'nunique'
    }).reset_index()
    market_data.columns = ['Market', 'Avg_Price', 'Price_Std', 'Total_Arrivals', 'Commodity_Count']
    
    # Market volume vs price variation
    fig_geo = px.scatter(
        market_data,
        x='Total_Arrivals',
        y='Price_Std',
        size='Commodity_Count',
        color='Avg_Price',
        hover_name='Market',
        title='Market Comparison: Volume vs Price Variation',
        labels={
            'Total_Arrivals': 'Total Volume',
            'Price_Std': 'Price Variation',
            'Commodity_Count': 'Number of Commodities'
        }
    )
    st.plotly_chart(fig_geo, use_container_width=True)
    
    # Market rankings
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top Markets by Volume")
        st.dataframe(market_data.nlargest(5, 'Total_Arrivals')[['Market', 'Total_Arrivals']])
    
    with col2:
        st.subheader("Most Diverse Markets")
        st.dataframe(market_data.nlargest(5, 'Commodity_Count')[['Market', 'Commodity_Count']])

# Footer
st.markdown("---")
st.markdown("*Data insights powered by advanced analytics*")
