import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Set page configuration
st.set_page_config(
    page_title="Pharmacy License Dashboard",
    page_icon="💊",
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

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('sales_license_2024_10.csv')
    return df

# Main title
st.title("📊 Pharmacy License Analytics Dashboard")
st.markdown("---")

# Load the data
df = load_data()

# Sidebar filters
st.sidebar.header("Filters")
selected_district = st.sidebar.multiselect(
    "Select District",
    options=sorted(df['mfg_districtname'].unique()),
    default=sorted(df['mfg_districtname'].unique())[:5]
)

selected_license = st.sidebar.multiselect(
    "Select License Type",
    options=sorted(df['licensename'].unique()),
    default=sorted(df['licensename'].unique())
)

# Filter the data
filtered_df = df[
    (df['mfg_districtname'].isin(selected_district)) &
    (df['licensename'].isin(selected_license))
]

# Top metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Licenses", len(filtered_df))
with col2:
    st.metric("Districts", filtered_df['mfg_districtname'].nunique())
with col3:
    st.metric("Business Types", filtered_df['constitution_particulars'].nunique())
with col4:
    st.metric("License Types", filtered_df['licensename'].nunique())

st.markdown("---")

# Create two columns for charts
col1, col2 = st.columns(2)

with col1:
    # License Type Distribution
    st.subheader("License Type Distribution")
    license_dist = filtered_df['licensename'].value_counts()
    fig_license = px.pie(
        values=license_dist.values,
        names=license_dist.index,
        hole=0.4
    )
    fig_license.update_layout(height=400)
    st.plotly_chart(fig_license, use_container_width=True)

with col2:
    # Business Constitution Distribution
    st.subheader("Business Types")
    constitution_dist = filtered_df['constitution_particulars'].value_counts()
    fig_constitution = px.bar(
        x=constitution_dist.index,
        y=constitution_dist.values,
        labels={'x': 'Business Type', 'y': 'Count'}
    )
    fig_constitution.update_layout(height=400)
    st.plotly_chart(fig_constitution, use_container_width=True)

# District Analysis
st.markdown("---")
st.subheader("District-wise Analysis")
district_data = filtered_df['mfg_districtname'].value_counts().head(10)
fig_district = px.bar(
    x=district_data.index,
    y=district_data.values,
    labels={'x': 'District', 'y': 'Number of Licenses'}
)
st.plotly_chart(fig_district, use_container_width=True)

# Detailed Data View
st.markdown("---")
st.subheader("Detailed Data View")
st.dataframe(
    filtered_df[['name_frim', 'licensename', 'constitution_particulars', 'mfg_districtname', 'license_validity']],
    hide_index=True
)

# Add export functionality
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    "Download Data as CSV",
    csv,
    "pharmacy_licenses.csv",
    "text/csv",
    key='download-csv'
)
