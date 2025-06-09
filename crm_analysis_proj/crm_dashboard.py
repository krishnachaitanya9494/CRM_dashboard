import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Load Data
@st.cache_data  # Cache to improve performance
def load_data():
    return pd.read_csv("data/data.csv")

df = load_data()

# Fix Date Parsing
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], format="%d-%m-%Y %H:%M", errors='coerce')

# Sidebar - Date and Country Selection
st.sidebar.header("📅 Select Date Range and Country")
start_date = st.sidebar.date_input("Start Date", df["InvoiceDate"].min().date())
end_date = st.sidebar.date_input("End Date", df["InvoiceDate"].max().date())

# Country Selection Dropdown
country_list = df['Country'].dropna().unique().tolist()
selected_country = st.sidebar.selectbox("Select Country", ["All"] + country_list)

# Filter Data by Date Range and Country
df_filtered = df[(df["InvoiceDate"].dt.date >= start_date) & (df["InvoiceDate"].dt.date <= end_date)]
if selected_country != "All":
    df_filtered = df_filtered[df_filtered['Country'] == selected_country]

# KPI Metrics
df_filtered['Revenue'] = df_filtered['UnitPrice'] * df_filtered['Quantity']
total_revenue = df_filtered['Revenue'].sum()
new_customers = df_filtered['CustomerID'].nunique()
avg_order_value = df_filtered['Revenue'].mean()

# Corrected Churn Rate Calculation
total_customers = df['CustomerID'].nunique()
churn_rate = round(((total_customers - new_customers) / total_customers) * 100, 1) if total_customers > 0 else 0

# Header
st.markdown("""
    <h1 style="text-align: center; font-size: 36px; font-weight: bold;">E-Commerce CRM Analysis</h1>
    <style>
        .css-18e3th9 { padding: 0px !important; }
        .block-container { padding-top: 0px !important; }
    </style>
""", unsafe_allow_html=True)

# Navigation Tabs
tabs = st.tabs(["Overview", "RFM Analysis", "Churn Prediction", "Customer Segmentation"])

# ---- OVERVIEW TAB ----
with tabs[0]:
    col1, col2, col3, col4 = st.columns(4)

    # Display KPI Cards
    col1.metric("💰 Total Revenue", f"${total_revenue:,.2f}")
    col2.metric("🧑‍💼 New Customers", f"{new_customers}")
    col3.metric("📦 Avg Order Value", f"${avg_order_value:.2f}")
    col4.metric("📉 Churn Rate", f"{churn_rate}%")

    # Revenue Overview Bar Chart
    category_revenue = df_filtered.groupby('Category')['Revenue'].sum().reset_index()
    revenue_chart = px.bar(category_revenue, x='Category', y='Revenue', title="Revenue Overview",
                           color_discrete_sequence=["#7ED321"], labels={"Revenue": "$ Revenue"})
    st.plotly_chart(revenue_chart, use_container_width=True)

    # Country Overview Bar Chart
    country_revenue = df_filtered.groupby('Country')['Revenue'].sum().reset_index()
    country_chart = px.bar(country_revenue, x='Country', y='Revenue', title="Revenue by Country",
                           color_discrete_sequence=["#F39C12"], labels={"Revenue": "$ Revenue"})
    st.plotly_chart(country_chart, use_container_width=True)

    # Recent Sales
    recent_sales = df_filtered[['CustomerID', 'StockCode', 'InvoiceDate', 'Revenue']].tail(5)
    st.subheader("🛒 Recent Sales")
    st.table(recent_sales)

# ---- RFM ANALYSIS TAB ----
with tabs[1]:
    today = pd.to_datetime("today")

    # Calculate RFM Metrics
    df_filtered['Recency'] = (today - df_filtered.groupby('CustomerID')['InvoiceDate'].transform('max')).dt.days
    frequency = df_filtered.groupby('CustomerID')['InvoiceNo'].nunique()
    monetary = df_filtered.groupby('CustomerID')['Revenue'].sum()

    rfm_df = pd.DataFrame({
        'Recency': df_filtered.groupby('CustomerID')['Recency'].min(),
        'Frequency': frequency,
        'Monetary': monetary
    }).reset_index()

    # Dynamic Binning Function
    def dynamic_qcut(column, num_bins=4):
        unique_values = column.nunique()
        bins = min(num_bins, unique_values)
        labels = list(range(1, bins + 1))
        try:
            return pd.qcut(column, bins, labels=labels, duplicates='drop')
        except ValueError:
            return pd.Series([1] * len(column), index=column.index)

    # Apply binning
    rfm_df['R'] = dynamic_qcut(rfm_df['Recency'])
    rfm_df['F'] = dynamic_qcut(rfm_df['Frequency'])
    rfm_df['M'] = dynamic_qcut(rfm_df['Monetary'])

    rfm_df['RFM_Score'] = rfm_df['R'].astype(str) + rfm_df['F'].astype(str) + rfm_df['M'].astype(str)

    # RFM Segments Pie Chart
    rfm_segments = rfm_df['RFM_Score'].value_counts().reset_index()
    rfm_segments.columns = ['RFM Segment', 'Count']
    rfm_segment_pie = px.pie(rfm_segments, names='RFM Segment', values='Count', title="RFM Segments Distribution")
    st.plotly_chart(rfm_segment_pie, use_container_width=True)

# ---- CHURN PREDICTION TAB ----
with tabs[2]:
    st.header("📉 Churn Prediction")
    churn_threshold = 90
    df_filtered['Days_Since_Last_Purchase'] = (today - df_filtered['InvoiceDate']).dt.days
    churned_customers = df_filtered[df_filtered['Days_Since_Last_Purchase'] > churn_threshold]['CustomerID'].nunique()

    st.metric("🚨 Churned Customers", churned_customers)

    churn_data = df_filtered.groupby('CustomerID')['Days_Since_Last_Purchase'].max().reset_index()
    churn_data['Churn'] = churn_data['Days_Since_Last_Purchase'] > churn_threshold
    churn_pie = px.pie(churn_data, names='Churn', title="Churn Distribution")
    st.plotly_chart(churn_pie, use_container_width=True)

# ---- CUSTOMER SEGMENTATION TAB ----
with tabs[3]:
    st.header("👥 Customer Segmentation")

    rfm_scaled = StandardScaler().fit_transform(rfm_df[['Recency', 'Frequency', 'Monetary']])
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    rfm_df['Cluster'] = kmeans.fit_predict(rfm_scaled)

    cluster_distribution = rfm_df['Cluster'].value_counts().reset_index()
    cluster_distribution.columns = ['Cluster', 'Count']
    cluster_pie = px.pie(cluster_distribution, names='Cluster', values='Count', title="Customer Segmentation Clusters")
    st.plotly_chart(cluster_pie, use_container_width=True)

    cluster_characteristics = rfm_df.groupby('Cluster').mean().reset_index()
    st.subheader("📊 Cluster Characteristics")
    st.table(cluster_characteristics)

# Footer
st.markdown("""
    <div style="text-align: right;">
        <button style="padding: 10px 20px; background-color: black; color: white; border-radius: 5px;">⬇ Export</button>
    </div>
""", unsafe_allow_html=True)
