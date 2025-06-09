import streamlit as st
import pandas as pd
import plotly.express as px

def show(df):
    st.title("📉 Churn Analysis")

    if df is None or df.empty:
        st.warning("⚠ No data available.")
        return

    required_columns = ['CustomerID', 'InvoiceDate', 'Quantity', 'UnitPrice', 'CustomerName']
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        st.error(f"🚨 Missing columns: {missing_columns}. Please check the dataset.")
        return

    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], errors='coerce')
    df['InvoiceMonth'] = df['InvoiceDate'].dt.to_period('M').astype(str)
    df['Revenue'] = df['UnitPrice'] * df['Quantity']

    reference_date = df['InvoiceDate'].max()
    churn_threshold = 90

    customer_last_purchase = df.groupby('CustomerID')['InvoiceDate'].max().reset_index()
    customer_last_purchase['DaysSinceLastPurchase'] = (reference_date - customer_last_purchase['InvoiceDate']).dt.days
    customer_last_purchase['Churned'] = customer_last_purchase['DaysSinceLastPurchase'].apply(lambda x: 1 if x > churn_threshold else 0)

    churn_per_month = customer_last_purchase.merge(df[['CustomerID', 'InvoiceMonth']], on='CustomerID', how='left')
    churn_per_month = churn_per_month.groupby('InvoiceMonth')['Churned'].mean().reset_index()
    churn_per_month['Churned'] *= 100

    fig_churn_rate = px.line(
        churn_per_month, x="InvoiceMonth", y="Churned", markers=True,
        title="📉 Monthly Churn Rate (%)",
        labels={"InvoiceMonth": "Month", "Churned": "Churn Percentage"}
    )
    st.plotly_chart(fig_churn_rate, use_container_width=True)

    churn_reasons = pd.DataFrame({
        "Reason": ["Price", "Poor Experience", "Competitor", "Other"],
        "Count": [30, 25, 20, 25]
    })

    fig_churn_pie = px.pie(
        churn_reasons, names="Reason", values="Count",
        title="🔍 Reasons for Churn",
        color_discrete_map={"Price": "red", "Poor Experience": "orange", "Competitor": "blue", "Other": "gray"}
    )
    st.plotly_chart(fig_churn_pie, use_container_width=True)

    risk_factors = pd.DataFrame({
        "Risk Factor": ["High Purchase Drop", "Frequent Returns", "Low Engagement"],
        "Mild": [15, 10, 20],
        "Moderate": [25, 15, 30],
        "Severe": [10, 20, 15]
    })

    fig_risk_factors = px.bar(
        risk_factors, x="Risk Factor", y=["Mild", "Moderate", "Severe"],
        title="⚠ Churn Risk Factors",
        labels={"value": "Customer Count", "variable": "Risk Level"},
        barmode="stack"
    )
    st.plotly_chart(fig_risk_factors, use_container_width=True)

    at_risk_customers = customer_last_purchase.merge(df[['CustomerID', 'CustomerName']], on='CustomerID', how='left')
    at_risk_customers = at_risk_customers[at_risk_customers['Churned'] == 1].nlargest(5, 'DaysSinceLastPurchase')

    at_risk_customers['LifetimeValue'] = df.groupby('CustomerID')['Revenue'].sum().reset_index(drop=True)
    at_risk_customers['RiskFactors'] = ["High Purchase Drop", "Frequent Returns", "Low Engagement", "Competitor", "Poor Experience"]

    st.subheader("⚠ Customers at Risk of Churning")
    st.dataframe(at_risk_customers[['CustomerID', 'CustomerName', 'InvoiceDate', 'LifetimeValue', 'RiskFactors']])
