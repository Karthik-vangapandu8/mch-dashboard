import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Set page config
st.set_page_config(page_title="EV & Real Estate Analysis", layout="wide")

# Load EV data
@st.cache_data
def load_ev_data():
    df = pd.read_csv('ts_transport_registration_01_11_2024to30_11_2024.csv')
    df['fromdate'] = pd.to_datetime(df['fromdate'], format='%d/%m/%Y')
    return df

# Example real estate price ranges for different areas (you can replace with actual data)
real_estate_prices = {
    'RTA RANGAREDDY': {'avg_price_sqft': 6500, 'growth_rate': 12.5},
    'RTA-HYDERABAD-CZ': {'avg_price_sqft': 8500, 'growth_rate': 15.2},
    'RTA UPPAL': {'avg_price_sqft': 5500, 'growth_rate': 10.8},
    'RTA MEDCHAL': {'avg_price_sqft': 4800, 'growth_rate': 9.5},
    'RTA IBRAHIMPATNAM': {'avg_price_sqft': 4200, 'growth_rate': 8.7},
    'RTA-HYDERABAD-NZ': {'avg_price_sqft': 7500, 'growth_rate': 14.3},
    'RTA-HYDERABAD-SZ': {'avg_price_sqft': 7200, 'growth_rate': 13.8},
    'RTA-HYDERABAD-WZ': {'avg_price_sqft': 7800, 'growth_rate': 14.7},
    'UNIT OFFICE KUKATPALLY': {'avg_price_sqft': 6200, 'growth_rate': 11.5},
    'UNIT OFFICE PATANCHERUVU': {'avg_price_sqft': 4500, 'growth_rate': 9.2}
}

try:
    # Load data
    df = load_ev_data()
    
    # Filter EV data
    ev_data = df[df['fuel'].str.contains('BATTERY', na=False)]
    
    st.title("🚗🏠 EV Registration & Real Estate Analysis")
    st.markdown("""
    This dashboard analyzes the relationship between EV registrations and real estate trends in Telangana.
    """)
    
    # Create combined dataset
    ev_by_office = ev_data.groupby('OfficeCd').size().reset_index(name='ev_count')
    total_by_office = df.groupby('OfficeCd').size().reset_index(name='total_registrations')
    
    combined_data = pd.merge(ev_by_office, total_by_office, on='OfficeCd')
    combined_data['ev_percentage'] = (combined_data['ev_count'] / combined_data['total_registrations'] * 100).round(2)
    
    # Add real estate data
    combined_data['avg_price_sqft'] = combined_data['OfficeCd'].map(
        {k: v['avg_price_sqft'] for k, v in real_estate_prices.items()}
    )
    combined_data['price_growth'] = combined_data['OfficeCd'].map(
        {k: v['growth_rate'] for k, v in real_estate_prices.items()}
    )
    
    # Key Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total EV Registrations", f"{len(ev_data):,}")
    with col2:
        st.metric("Average EV %", f"{(len(ev_data)/len(df)*100):.2f}%")
    with col3:
        correlation = combined_data['ev_count'].corr(combined_data['avg_price_sqft'])
        st.metric("EV-Price Correlation", f"{correlation:.2f}")
    
    # Main Analysis
    tab1, tab2, tab3 = st.tabs(["📊 Area Analysis", "💰 Price Correlation", "📈 Growth Patterns"])
    
    with tab1:
        st.subheader("Area-wise EV Adoption vs Real Estate Prices")
        
        # Scatter plot
        fig = px.scatter(
            combined_data,
            x='avg_price_sqft',
            y='ev_percentage',
            size='total_registrations',
            color='price_growth',
            hover_data=['OfficeCd'],
            title='EV Adoption vs Real Estate Prices',
            labels={
                'avg_price_sqft': 'Average Price per Sq.ft (₹)',
                'ev_percentage': 'EV Adoption Rate (%)',
                'price_growth': 'Real Estate Price Growth (%)'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Area comparison
        col1, col2 = st.columns(2)
        with col1:
            top_ev = combined_data.nlargest(5, 'ev_percentage')
            fig_top_ev = px.bar(
                top_ev,
                x='OfficeCd',
                y='ev_percentage',
                title='Top 5 Areas by EV Adoption'
            )
            st.plotly_chart(fig_top_ev, use_container_width=True)
        
        with col2:
            top_price = combined_data.nlargest(5, 'avg_price_sqft')
            fig_top_price = px.bar(
                top_price,
                x='OfficeCd',
                y='avg_price_sqft',
                title='Top 5 Areas by Real Estate Prices'
            )
            st.plotly_chart(fig_top_price, use_container_width=True)
    
    with tab2:
        st.subheader("Price Range Analysis")
        
        # Create price brackets
        combined_data['price_bracket'] = pd.qcut(combined_data['avg_price_sqft'], q=4, labels=[
            'Budget (₹4000-5000/sqft)',
            'Mid-Range (₹5000-6000/sqft)',
            'Premium (₹6000-7500/sqft)',
            'Luxury (>₹7500/sqft)'
        ])
        
        # Average EV adoption by price bracket
        ev_by_bracket = combined_data.groupby('price_bracket')['ev_percentage'].mean().reset_index()
        fig_brackets = px.bar(
            ev_by_bracket,
            x='price_bracket',
            y='ev_percentage',
            title='Average EV Adoption by Property Price Range',
            labels={'ev_percentage': 'Average EV Adoption Rate (%)'}
        )
        st.plotly_chart(fig_brackets, use_container_width=True)
        
        # Detailed area analysis
        st.dataframe(
            combined_data[['OfficeCd', 'ev_percentage', 'avg_price_sqft', 'price_growth']]
            .sort_values('ev_percentage', ascending=False)
            .style.format({
                'ev_percentage': '{:.2f}%',
                'avg_price_sqft': '₹{:,.0f}',
                'price_growth': '{:.1f}%'
            })
        )
    
    with tab3:
        st.subheader("Growth Pattern Analysis")
        
        # Create growth categories
        combined_data['growth_category'] = pd.qcut(combined_data['price_growth'], q=3, labels=[
            'Steady Growth (<10%)',
            'Moderate Growth (10-13%)',
            'High Growth (>13%)'
        ])
        
        # EV adoption by growth category
        ev_by_growth = combined_data.groupby('growth_category')['ev_percentage'].mean().reset_index()
        fig_growth = px.bar(
            ev_by_growth,
            x='growth_category',
            y='ev_percentage',
            title='EV Adoption by Real Estate Growth Rate',
            labels={'ev_percentage': 'Average EV Adoption Rate (%)'}
        )
        st.plotly_chart(fig_growth, use_container_width=True)
        
        # Growth patterns
        col1, col2 = st.columns(2)
        with col1:
            # High growth areas
            high_growth = combined_data[combined_data['price_growth'] > 13]
            fig_high = px.scatter(
                high_growth,
                x='price_growth',
                y='ev_percentage',
                size='total_registrations',
                title='High Growth Areas',
                labels={
                    'price_growth': 'Real Estate Growth Rate (%)',
                    'ev_percentage': 'EV Adoption Rate (%)'
                }
            )
            st.plotly_chart(fig_high, use_container_width=True)
        
        with col2:
            # Emerging areas (high EV, lower prices)
            emerging = combined_data[
                (combined_data['ev_percentage'] > combined_data['ev_percentage'].median()) &
                (combined_data['avg_price_sqft'] < combined_data['avg_price_sqft'].median())
            ]
            fig_emerging = px.scatter(
                emerging,
                x='avg_price_sqft',
                y='ev_percentage',
                size='price_growth',
                title='Emerging Areas (High EV Adoption, Lower Prices)',
                labels={
                    'avg_price_sqft': 'Average Price per Sq.ft (₹)',
                    'ev_percentage': 'EV Adoption Rate (%)'
                }
            )
            st.plotly_chart(fig_emerging, use_container_width=True)
    
    # Investment Insights
    st.header("💡 Investment Insights")
    
    # Find emerging areas
    emerging_areas = combined_data[
        (combined_data['ev_percentage'] > combined_data['ev_percentage'].median()) &
        (combined_data['avg_price_sqft'] < combined_data['avg_price_sqft'].median()) &
        (combined_data['price_growth'] > combined_data['price_growth'].median())
    ]
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Emerging Investment Areas")
        for _, row in emerging_areas.iterrows():
            st.write(f"""
            **{row['OfficeCd']}**
            - EV Adoption: {row['ev_percentage']:.2f}%
            - Current Price: ₹{row['avg_price_sqft']:,.0f}/sqft
            - Growth Rate: {row['price_growth']:.1f}%
            """)
    
    with col2:
        st.subheader("Market Indicators")
        st.write(f"""
        - Areas with highest EV growth typically show {combined_data['price_growth'].max():.1f}% real estate appreciation
        - Premium areas (>₹7500/sqft) show {combined_data[combined_data['avg_price_sqft'] > 7500]['ev_percentage'].mean():.2f}% EV adoption
        - Emerging areas show potential for {emerging_areas['price_growth'].mean():.1f}% annual growth
        """)

except Exception as e:
    st.error(f"Error in analysis: {str(e)}")
    st.markdown("""
    Please ensure:
    1. The EV registration data file is present
    2. Real estate data is accurately mapped
    3. All required columns are available
    """)
