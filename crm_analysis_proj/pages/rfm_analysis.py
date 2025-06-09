import streamlit as st
import pandas as pd
import plotly.express as px

def show(df):
    st.title("📊 RFM Analysis & Customer Segmentation")

    if df is None or df.empty:
        st.warning("⚠ No data available.")
        return

    required_columns = ['CustomerID', 'CustomerName', 'InvoiceDate', 'Quantity', 'UnitPrice']
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        st.error(f"🚨 Missing columns: {missing_columns}. Please check the dataset.")
        return

    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], errors='coerce')
    df['Revenue'] = df['UnitPrice'] * df['Quantity']

    reference_date = df['InvoiceDate'].max()
    rfm = df.groupby(['CustomerID', 'CustomerName']).agg({
        'InvoiceDate': lambda x: (reference_date - x.max()).days,
        'InvoiceNo': 'nunique',
        'Revenue': 'sum'
    }).reset_index()

    rfm.columns = ['CustomerID', 'CustomerName', 'Recency', 'Frequency', 'Monetary']
    rfm = rfm.dropna()

    try:
        rfm['R'] = pd.qcut(rfm['Recency'], q=4, labels=[4, 3, 2, 1]).astype(int)
        rfm['F'] = pd.qcut(rfm['Frequency'].rank(method="first"), q=4, labels=[1, 2, 3, 4]).astype(int)
        rfm['M'] = pd.qcut(rfm['Monetary'].rank(method="first"), q=4, labels=[1, 2, 3, 4]).astype(int)
        rfm['RFM Score'] = rfm[['R', 'F', 'M']].sum(axis=1)
    except ValueError as e:
        st.error(f"🚨 Error in RFM segmentation: {e}")
        return

    def segment_customer(score):
        if score >= 9:
            return "Loyal Customers"
        elif score >= 6:
            return "New Customers"
        elif score >= 4:
            return "Hibernating"
        else:
            return "Churned"

    rfm['Segment'] = rfm['RFM Score'].apply(segment_customer)

    st.write("### 🔍 RFM Data")
    st.dataframe(rfm.head())

    avg_rfm = rfm.groupby("Segment")[["Recency", "Frequency", "Monetary"]].mean().reset_index()
    fig_rfm_bar = px.bar(
        avg_rfm.melt(id_vars=["Segment"], var_name="RFM Metric", value_name="Average Value"),
        x="Segment", y="Average Value", color="RFM Metric",
        title="📊 RFM Value Distribution (Stacked Bar Chart)",
        barmode="stack"
    )
    st.plotly_chart(fig_rfm_bar, use_container_width=True)

    segment_counts = rfm['Segment'].value_counts().reset_index()
    segment_counts.columns = ['Segment', 'Count']
    fig_segment_pie = px.pie(segment_counts, names="Segment", values="Count", title="📌 Customer Segmentation Breakdown")
    st.plotly_chart(fig_segment_pie, use_container_width=True)

    if 'RFM Score' in rfm.columns:
        top_customers = rfm[['CustomerID', 'CustomerName', 'Recency', 'Frequency', 'Monetary', 'Segment', 'RFM Score']].sort_values(by="RFM Score", ascending=False)
        st.subheader("🏆 Top Customers Based on RFM Score")
        st.dataframe(top_customers.head(10))
    else:
        st.warning("⚠ 'RFM Score' is missing. Check dataset calculations.")

    return rfm
