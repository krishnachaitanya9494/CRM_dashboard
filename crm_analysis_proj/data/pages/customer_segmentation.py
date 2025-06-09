import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def show(df):
    st.title("🧑‍🤝‍🧑 Customer Segmentation")

    # ✅ **Step 1: Data Preprocessing**
    if df is None or df.empty:
        st.warning("⚠ No data available.")
        return

    required_columns = ['CustomerID', 'InvoiceDate', 'Quantity', 'UnitPrice']
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        st.error(f"🚨 Missing columns: {missing_columns}. Please check the dataset.")
        return

    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], errors='coerce')
    df['Revenue'] = df['UnitPrice'] * df['Quantity']

    # ✅ **Step 2: Feature Engineering**
    reference_date = df['InvoiceDate'].max()

    customer_features = df.groupby('CustomerID').agg({
        'InvoiceDate': lambda x: (reference_date - x.max()).days,  # Recency
        'InvoiceNo': 'nunique',  # Frequency
        'Revenue': 'sum'  # Monetary Value
    }).reset_index()

    customer_features.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']

    # Handle missing values
    customer_features = customer_features.dropna()

    # ✅ **Step 3: Data Scaling**
    scaler = StandardScaler()
    customer_features_scaled = scaler.fit_transform(customer_features[['Recency', 'Frequency', 'Monetary']])

    # ✅ **Step 4: K-Means Clustering**
    kmeans = KMeans(n_clusters=4, random_state=42)
    customer_features['Segment'] = kmeans.fit_predict(customer_features_scaled)

    # ✅ **Step 5: Assigning Segment Labels**
    segment_map = {
        0: "Loyal Customers",
        1: "New Customers",
        2: "Hibernating",
        3: "High Value"
    }
    customer_features['Segment'] = customer_features['Segment'].map(segment_map)

    # ✅ **Step 6: Customer Segmentation Pie Chart**
    segment_counts = customer_features['Segment'].value_counts().reset_index()
    segment_counts.columns = ['Segment', 'Count']

    fig_segment_pie = px.pie(
        segment_counts, names="Segment", values="Count",
        title="🧩 Customer Segmentation",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(fig_segment_pie, use_container_width=True)

    # ✅ **Step 7: Display Segmented Customers Table**
    st.subheader("📋 Customer Segments Data")
    st.dataframe(customer_features)

    return customer_features
